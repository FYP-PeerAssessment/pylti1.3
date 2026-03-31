"""Exception types raised by the LTI launch and service flow."""

import requests


class LtiException(Exception):
    """Base exception for tool-side LTI failures."""

    pass


class LtiConfigurationException(LtiException):
    """Raised when the tool/platform configuration is invalid."""

    pass


class OIDCException(LtiException):
    """Raised when the OIDC login request is invalid."""

    pass


class LtiServiceException(LtiException):
    """Wraps failed outbound service calls to the platform."""

    def __init__(self, message: str, response: requests.Response):
        msg = f"{message} HTTP response [{response.url}]: {response.status_code}"
        super().__init__(msg)
        self.response = response
