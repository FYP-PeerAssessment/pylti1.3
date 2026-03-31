"""Helpers for the LTI dynamic registration flow."""

from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import requests
from requests.exceptions import RequestException

from .exception import LtiException, LtiServiceException


def generate_key_pair(key_size: int = 4096) -> tuple[str, str]:
    """
    Generate a PEM-encoded RSA private/public key pair.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()

    private_key_str = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    public_key_str = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    return private_key_str, public_key_str


class DynamicRegistration:
    """
    Controls the platform-driven LTI dynamic registration flow.
    """

    client_name = ""
    description = ""
    response_types = ["id_token"]
    grant_types = ["implicit", "client_credentials"]

    def get_request_session(self) -> requests.Session:
        return requests.Session()

    def get_client_name(self) -> str:
        return self.client_name

    def get_response_types(self) -> list[str]:
        return self.response_types

    def get_grant_types(self) -> list[str]:
        return self.grant_types

    def get_initiate_login_uri(self) -> str:
        raise NotImplementedError

    def get_jwks_uri(self) -> str:
        raise NotImplementedError

    def get_redirect_uris(self) -> list[str]:
        raise NotImplementedError

    def get_scopes(self) -> list[str]:
        return []

    def get_domain(self) -> str:
        raise NotImplementedError

    def get_target_link_uri(self) -> str:
        raise NotImplementedError

    def get_claims(self) -> list[str]:
        return ["sub"]

    def get_messages(self) -> list[dict[str, str]]:
        return []

    def get_description(self) -> str:
        return self.description

    def get_logo_uri(self) -> str:
        raise NotImplementedError

    def lti_registration_data(self) -> dict[str, Any]:
        return {
            "response_types": self.get_response_types(),
            "application_type": "web",
            "client_name": self.get_client_name(),
            "initiate_login_uri": self.get_initiate_login_uri(),
            "grant_types": self.get_grant_types(),
            "jwks_uri": self.get_jwks_uri(),
            "token_endpoint_auth_method": "private_key_jwt",
            "redirect_uris": self.get_redirect_uris(),
            "scope": " ".join(self.get_scopes()),
            "https://purl.imsglobal.org/spec/lti-tool-configuration": {
                "domain": self.get_domain(),
                "target_link_uri": self.get_target_link_uri(),
                "claims": self.get_claims(),
                "messages": self.get_messages(),
                "description": self.get_description(),
            },
            "logo_uri": self.get_logo_uri(),
        }

    def get_openid_configuration_endpoint(self) -> str:
        raise NotImplementedError

    def get_registration_token(self) -> str | None:
        raise NotImplementedError

    def get_openid_configuration(self) -> dict[str, Any]:
        openid_configuration_endpoint = self.get_openid_configuration_endpoint()

        with self.get_request_session() as session:
            response = session.get(openid_configuration_endpoint)
            try:
                return response.json()
            except RequestException as err:
                raise LtiServiceException(
                    f"The OpenID configuration data is invalid: {err}",
                    response,
                ) from err
            except ValueError as err:
                raise LtiServiceException(
                    "The OpenID configuration data is invalid.",
                    response,
                ) from err

    def register(self) -> dict[str, Any]:
        openid_configuration_endpoint = self.get_openid_configuration_endpoint()
        registration_token = self.get_registration_token()

        if not openid_configuration_endpoint:
            raise LtiException("No OpenID configuration endpoint was specified.")

        openid_configuration = self.get_openid_configuration()

        with self.get_request_session() as session:
            assert "registration_endpoint" in openid_configuration, (
                "The OpenID config does not have a registration endpoint."
            )
            registration_endpoint = openid_configuration["registration_endpoint"]
            registration_data = self.lti_registration_data()

            headers = {"Accept": "application/json"}
            if registration_token is not None:
                headers["Authorization"] = "Bearer " + registration_token

            response = session.post(
                registration_endpoint,
                headers=headers,
                json=registration_data,
            )

            if not response.ok:
                raise LtiServiceException(
                    "The registration endpoint returned an error response.",
                    response,
                )

            try:
                openid_registration = response.json()
            except ValueError as err:
                raise LtiServiceException(
                    "The registration endpoint did not return a JSON object.",
                    response,
                ) from err

        conf_spec = "https://purl.imsglobal.org/spec/lti-platform-configuration"
        assert conf_spec in openid_configuration, "The OpenID config is not an LTI platform configuration"

        tool_spec = "https://purl.imsglobal.org/spec/lti-tool-configuration"
        assert tool_spec in openid_registration, "The OpenID registration is not an LTI tool configuration"

        return self.complete_registration(openid_configuration, openid_registration)

    def complete_registration(
        self,
        openid_configuration: dict[str, Any],
        openid_registration: dict[str, Any],
    ) -> Any:
        raise NotImplementedError

    def complete_html(self) -> str:
        return """
            <!doctype html>
            <html lang="en">
                <body>
                    <script>
                        (window.opener || window.parent).postMessage({subject:'org.imsglobal.lti.close'}, '*');
                    </script>
                    <p>The registration is now complete. You can close this window and return to the registered platform.</p>
                </body>
            </html>
        """
