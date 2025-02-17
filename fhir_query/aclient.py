import json
import logging
from typing import Literal
from urllib.parse import urlencode, urljoin

import aiohttp

from fhir_query.base import FhirClientBase
from fhir_query.bundle import FhirQueryBundle
from fhir_query.resource_types import ResourceType

logger = logging.getLogger(__name__)


class AsyncFhirQueryClient(FhirClientBase):
    """
    Async client for querying a FHIR server.
    """

    def __init__(
        self,
        base_url,
        use_post=False,
        headers=None,
        auth_method=None,
        login_url=None,
        username=None,
        password=None,
        session=None,
        token=None,
    ):
        self._headers = headers or {}
        self.session = None

        super().__init__(
            base_url=base_url,
            headers=headers,
            auth_method=auth_method,
            login_url=login_url,
            username=username,
            password=password,
            token=token,
        )

        self.use_post = use_post
        self.session = session

        # Handle async login auth after initialization
        if self.auth_method == "login":
            self._pending_login_auth = True
        else:
            self._pending_login_auth = False

    def _get_headers(self) -> dict:
        """Get the current headers dictionary."""
        return self._headers

    async def ensure_auth(self):
        """Ensure authentication is set up"""
        if self._pending_login_auth and self.login_url:
            await self._setup_login_auth(self.login_url)
            self._pending_login_auth = False

    async def get(
        self,
        resource_type: ResourceType,
        params: dict = None,
        full_url: bool = False,
        search_string: str = None,
        use_post: bool = False,
        pages: int = None,
        headers: dict = None,
    ):
        """
        Get a resource from the FHIR server asynchronously.
        """
        await self.ensure_auth()
        return await self._get(
            resource_type, params, full_url, search_string, use_post, pages, headers
        )

    async def _get(
        self,
        resource_type: ResourceType,
        params: dict = None,
        full_url: bool = False,
        search_string: str = None,
        use_post: bool = False,
        pages: int = None,
        headers: dict = None,
    ):
        """
        Get a resource from the FHIR server asynchronously.
        """
        logger.debug(
            "Making FHIR request - resource_type: %s, params: %s, full_url: %s, search_string: %s, use_post: %s, pages: %s",
            resource_type,
            params,
            full_url,
            search_string,
            use_post,
            pages,
        )

        # Ensure only one of params, search_string or full_url is provided
        provided_options = sum(
            [params is not None, search_string is not None, full_url is True]
        )
        assert (
            provided_options <= 1
        ), "Only one of the following should be provided: params, search_string or full_url"

        request_headers = {**self._headers, **(headers or {})}

        if full_url:
            logger.debug("Making request with full URL: %s", full_url)
            response_data = await self.make_request(
                method="GET",
                url=full_url,
                headers=request_headers,
            )
            return FhirQueryBundle(response_data)

        search_params = None

        if params:
            search_params = urlencode(params)
        elif search_string:
            search_params = search_string

        if use_post or self.use_post:
            logger.debug(
                "Making POST request to %s with params: %s",
                resource_type,
                search_params,
            )
            search_params = json.dumps(search_params) if search_params else None
            response_data = await self.make_request(
                method="POST",
                url=urljoin(self.base_url, f"{resource_type}/_search"),
                data=search_params,
                headers=request_headers,
            )
        else:
            url = urljoin(self.base_url, f"{resource_type}")
            if search_params:
                url = f"{url}?{search_params}"
            logger.debug("Making GET request to: %s", url)
            response_data = await self.make_request(
                method="GET",
                url=url,
                headers=request_headers,
            )

        fqc_bundle = FhirQueryBundle(response_data)

        if pages and pages > 1:
            remaining_pages = pages - 1
            while remaining_pages > 0:
                next_link = fqc_bundle.next_link
                if not next_link:
                    break
                response_data = await self.make_request(
                    method="GET",
                    url=next_link,
                    headers=request_headers,
                )
                fqc_bundle.add_bundle(response_data)
                remaining_pages -= 1

        return fqc_bundle

    async def make_request(
        self,
        method: Literal["GET", "POST"],
        url: str,
        data: dict = None,
        headers: dict = None,
    ):
        """
        Make an async request to the FHIR server.
        """
        logger.debug(
            "Making %s request to %s with headers: %s, data: %s",
            method,
            url,
            headers,
            data,
        )
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, json=data, headers=headers
            ) as response:
                response.raise_for_status()
                response_data = await response.json()
                logger.debug("Received response with status %d", response.status)
                return response_data

    async def _setup_login_auth(self, login_url=None):
        """Setup login authentication by making a request to the login URL with credentials."""
        logger.debug("Configuring login auth with username and password")
        if not self.username or not self.password:
            raise ValueError(
                "Username and password are required for login authentication."
            )
        if not login_url and not self.login_url:
            raise ValueError("login_url is required for login authentication")

        url = login_url or self.login_url
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                auth=aiohttp.BasicAuth(self.username, self.password),
                headers=self._headers,
            ) as response:
                response.raise_for_status()
                try:
                    # First try to parse as JSON
                    self.token = await response.json()
                except aiohttp.ContentTypeError:
                    # If that fails, get as text
                    self.token = await response.text()
                logger.info("Login authentication successful")
                self._setup_token_auth(self.token)
