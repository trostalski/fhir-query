import base64
import logging
import os
from typing import Literal

import requests

logger = logging.getLogger(__name__)


class FhirClientBase:
    """Base class containing common functionality for FHIR clients."""

    def __init__(
        self,
        base_url: str,
        headers: dict = None,
        auth_method: Literal["basic", "token", "login"] = None,
        login_url: str = None,
        username: str = None,
        password: str = None,
        token: str = None,
    ):
        # Ensure base_url ends with a trailing slash
        if not base_url.endswith("/"):
            base_url += "/"
            logger.debug("Added trailing slash to base URL: %s", base_url)

        logger.debug("Initializing FHIR client with base URL: %s", base_url)
        logger.debug("Authentication method: %s", auth_method or "None")
        logger.debug("Headers provided: %s", "Yes" if headers else "No")

        self.base_url = base_url
        self.auth_method = auth_method or os.getenv("FHIR_AUTH_METHOD")
        self.login_url = login_url or os.getenv("FHIR_LOGIN_URL")
        self.username = username or os.getenv("FHIR_USERNAME")
        self.password = password or os.getenv("FHIR_PASSWORD")
        self.token = token or os.getenv("FHIR_TOKEN")
        self._headers = headers or {}

        self._setup_auth()

    def _setup_auth(self):
        logger.debug("Starting authentication setup")
        if self.auth_method == "basic" and self.username and self.password:
            logger.debug("Setting up basic authentication")
            self._setup_basic_auth(self.username, self.password)
        elif self.auth_method == "token" and self.token:
            logger.debug("Setting up token authentication")
            self._setup_token_auth(self.token)
        elif self.auth_method == "login" and self.login_url:
            logger.debug("Setting up login authentication")
            self._setup_login_auth(login_url=self.login_url)
        else:
            logger.debug(
                "No authentication method configured or missing required parameters"
            )

    def _setup_basic_auth(self, username: str, password: str):
        """Setup basic authentication."""
        logger.debug("Configuring basic auth headers with username: %s", username)
        auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
        self._get_headers()["Authorization"] = f"Basic {auth_string}"
        logger.debug("Basic auth headers configured successfully")

    def _setup_token_auth(self, token: str):
        """Setup token authentication."""
        logger.debug("Configuring token auth headers")
        self._get_headers()["Authorization"] = f"Bearer {token}"
        logger.debug("Token auth headers configured successfully")

    def _setup_login_auth(self, login_url):
        """Setup login authentication by making a request to the login URL with credentials."""
        logger.debug("Configuring login auth with username and password")
        if not self.username or not self.password:
            logger.debug("Missing username or password for login authentication")
            raise ValueError(
                "Username and password are required for login authentication."
            )

        logger.debug("Making login request to: %s", login_url)
        response = requests.get(
            login_url, auth=(self.username, self.password), headers=self._headers
        )
        try:
            response.raise_for_status()
            self.token = response.text
            logger.debug("Login request successful, token received")
            self._setup_token_auth(self.token)
            logger.info("Login authentication successful")
        except requests.exceptions.RequestException as e:
            logger.error("Login request failed: %s", str(e))
            raise
