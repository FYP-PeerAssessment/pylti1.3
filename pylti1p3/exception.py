"""Exception types raised by the LTI launch and service flow."""

import requests


class LtiException(Exception):
    """Base exception for tool-side LTI failures."""

    pass


class OIDCException(Exception):
    """Raised when the OIDC login request is invalid."""

    pass


class LtiServiceException(LtiException):
    """Wraps failed outbound service calls to the platform."""

    def __init__(self, response: requests.Response):
        msg = f"HTTP response [{response.url}]: {str(response.status_code)} - {response.text}"
        super().__init__(msg)
        self.response = response
