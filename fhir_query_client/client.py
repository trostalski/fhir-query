import base64
import json
import logging
from typing import Literal
from urllib.parse import urlencode, urljoin

from requests import Session

from fhir_query_client.base import FhirClientBase
from fhir_query_client.bundle import FQCBundle
from fhir_query_client.resource_types import ResourceType

logger = logging.getLogger(__name__)


class FhirQueryClient(FhirClientBase):
    """
    Client for querying a fhir server.
    """

    def __init__(
        self,
        base_url: str,
        use_post: bool = False,
        session: Session = None,
        headers: dict = None,
        auth_method: Literal["basic", "token", "login"] = None,
        login_url: str = None,
        username: str = None,
        password: str = None,
        token: str = None,
    ):
        self._headers = headers or {}
        self.session = session or Session()

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
        self.session.headers.update(self._headers)

        # Handle login auth after initialization
        if self.auth_method == "login":
            self._pending_login_auth = True
        else:
            self._pending_login_auth = False

    def ensure_auth(self):
        """Ensure authentication is set up"""
        if self._pending_login_auth and self.login_url:
            self._setup_login_auth(self.login_url)
            self._pending_login_auth = False

    def _get_headers(self) -> dict:
        return self.session.headers

    def get(
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
        Get a resource from the fhir server.
        """
        self.ensure_auth()
        return self._get(
            resource_type=resource_type,
            params=params,
            full_url=full_url,
            search_string=search_string,
            use_post=use_post,
            pages=pages,
            headers=headers,
        )

    def _get(
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
        Internal get method implementation
        """
        # Ensure only one of params, search_string or full_url is provided
        provided_options = sum(
            [params is not None, search_string is not None, full_url is True]
        )
        assert (
            provided_options <= 1
        ), "Only one of the following should be provided: params, search_string or full_url"

        if full_url:
            response = self.make_request(
                method="GET",
                url=full_url,
                headers=headers,
            )
            return FQCBundle(response)

        search_params = None

        if params:
            search_params = urlencode(params)
        elif search_string:
            search_params = search_string

        if use_post or self.use_post:
            search_params = json.dumps(search_params)
            response = self.make_request(
                method="POST",
                url=urljoin(self.base_url, f"{resource_type}/_search"),
                data=search_params,
                headers=headers,
            )
        else:
            url = urljoin(self.base_url, f"{resource_type}")
            if search_params:
                url = f"{url}?{search_params}"
            response = self.make_request(
                method="GET",
                url=url,
                headers=headers,
            )

        fqc_bundle = FQCBundle(response)

        if pages and pages > 1:
            remaining_pages = pages - 1
            while remaining_pages > 0:
                next_link = fqc_bundle.next_link
                if not next_link:
                    break
                response = self.make_request(method="GET", url=next_link)
                fqc_bundle.add_bundle(response)
                remaining_pages -= 1

        return fqc_bundle

    def make_request(
        self,
        method: Literal["GET", "POST"],
        url: str,
        data: dict = None,
        headers: dict = None,
    ):
        """
        Make a request to the fhir server.
        """
        response = self.session.request(method, url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def _setup_login_auth(self, login_url):
        """Setup login authentication by making a request to the login URL with credentials."""
        logger.debug("Configuring login auth with username and password")
        if not self.username or not self.password:
            raise ValueError(
                "Username and password are required for login authentication."
            )
        if not login_url and not self.login_url:
            raise ValueError("login_url is required for login authentication")

        url = login_url or self.login_url
        response = self.session.get(
            url, auth=(self.username, self.password), headers=self._headers
        )
        response.raise_for_status()
        self.token = response.text
        logger.info("Login authentication successful")
        self._setup_token_auth(self.token)
