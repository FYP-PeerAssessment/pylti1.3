"""Insecure FastAPI helpers for accepting any LTI platform in development."""
from __future__ import annotations

import collections
import typing as t

from pylti1p3.contrib.fastapi.message_launch import FastAPIMessageLaunch
from pylti1p3.contrib.fastapi.oidc_login import FastAPIOIDCLogin
from pylti1p3.deployment import Deployment
from pylti1p3.registration import Registration
from pylti1p3.tool_config.abstract import (
    IssuerToClientRelation,
    ToolConfAbstract,
)

DEFAULT_AUTH_LOGIN_URL = "http://localhost:8000/oidc/auth"
DEFAULT_AUTH_TOKEN_URL = "http://localhost:8000/oidc/token"
DEFAULT_DEPLOYMENT_ID = "insecure-deployment"
DEFAULT_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAuvEnCaUOy1l9gk3wjW3P
ib1dBc5g92+6rhvZZOsN1a77fdOqKsrjWG1lDu8kq2nL+wbAzR3DdEPVw/1WUwtr
/Q1d5m+7S4ciXT63pENs1EPwWmeN33O0zkGx8I7vdiOTSVoywEyUZe6UyS+ujLfs
Rc2ImeLP5OHxpE1yULEDSiMLtSvgzEaMvf2AkVq5EL5nLYDWXZWXUnpiT/f7iK47
Mp2iQd4KYYG7YZ7lMMPCMBuhej7SOtZQ2FwaBjvZiXDZ172sQYBCiBAmOR3ofTL6
aD2+HUxYztVIPCkhyO84mQ7W4BFsOnKW4WRfEySHXd2hZkFMgcFNXY3dA6de519q
lcrL0YYx8ZHpzNt0foEzUsgJd8uJMUVvzPZgExwcyIbv5jWYBg0ILgULo7ve7VXG
5lMwasW/ch2zKp7tTILnDJwITMjF71h4fn4dMTun/7MWEtSl/iFiALnIL/4/YY71
7cr4rmcG1424LyxJGRD9L9WjO8etAbPkiRFJUd5fmfqjHkO6fPxyWsMUAu8bfYdV
RH7qN/erfGHmykmVGgH8AfK9GLT/cjN4GHA29bK9jMed6SWdrkygbQmlnsCAHrw0
RA+QE0t617h3uTrSEr5vkbLz+KThVEBfH84qsweqcac/unKIZ0e2iRuyVnG4cbq8
HUdio8gJ62D3wZ0UvVgr4a0CAwEAAQ==
-----END PUBLIC KEY-----
"""

DEFAULT_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
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
ulPIuF1kMX+T25yN2aGo0I1m3Hba
-----END RSA PRIVATE KEY-----
"""


class InsecureToolConf(ToolConfAbstract):
    """Tool configuration that blindly accepts any issuer/client for development."""

    def __init__(
        self,
        *,
        public_key: str = DEFAULT_PUBLIC_KEY,
        private_key: str = DEFAULT_PRIVATE_KEY,
        auth_login_url: str = DEFAULT_AUTH_LOGIN_URL,
        auth_token_url: str = DEFAULT_AUTH_TOKEN_URL,
        auth_audience: str | None = None,
        default_deployment_id: str = DEFAULT_DEPLOYMENT_ID,
    ) -> None:
        self._public_key = public_key
        self._private_key = private_key
        self._auth_login_url = auth_login_url
        self._auth_token_url = auth_token_url
        self._auth_audience = auth_audience
        self._default_deployment_id = default_deployment_id
        # Treat all issuers as allowing many client IDs so we always get client_id from the request.
        self.issuers_relation_types = collections.defaultdict(
            lambda: IssuerToClientRelation.MANY_CLIENTS_IDS_PER_ISSUER
        )

    def _build_registration(self, iss: str, client_id: str | None) -> Registration:
        registration = (
            Registration()
            .set_issuer(iss)
            .set_client_id(client_id or iss)
            .set_auth_login_url(self._auth_login_url)
            .set_auth_token_url(self._auth_token_url)
            .set_auth_audience(self._auth_audience)
            .set_tool_public_key(self._public_key)
            .set_tool_private_key(self._private_key)
        )
        return registration

    def find_registration_by_issuer(
        self,
        iss: str,
        *,
        action=None,
        request=None,
        jwt_body: t.Mapping[str, t.Any] | None = None,
    ) -> Registration:
        client_id: str | None = None
        if jwt_body:
            aud = jwt_body.get("aud")
            if isinstance(aud, str):
                client_id = aud
            elif isinstance(aud, (list, tuple)) and aud:
                client_id = aud[0]
        return self._build_registration(iss, client_id)

    def find_registration_by_params(
        self,
        iss: str,
        client_id: str,
        *,
        action=None,
        request=None,
        jwt_body: t.Mapping[str, t.Any] | None = None,
    ) -> Registration:
        return self._build_registration(iss, client_id)

    def find_deployment(self, iss: str, deployment_id: str) -> Deployment | None:
        return Deployment().set_deployment_id(deployment_id or self._default_deployment_id)

    def find_deployment_by_params(
        self, iss: str, deployment_id: str, client_id: str | None
    ) -> Deployment | None:
        return Deployment().set_deployment_id(deployment_id or self._default_deployment_id)

    def check_iss_has_one_client(self, iss: str) -> bool:  # type: ignore[override]
        return False

    def check_iss_has_many_clients(self, iss: str) -> bool:  # type: ignore[override]
        return True


class InsecureFastAPIOIDCLogin(FastAPIOIDCLogin[InsecureToolConf]):
    """OIDC login helper that fabricates registrations for any platform."""

    def validate_oidc_login(self) -> Registration:  # type: ignore[override]
        iss = self._get_request_param("iss")
        if not iss:
            raise Exception("Could not find issuer")

        client_id = self._get_request_param("client_id") or iss
        registration = self._tool_config.find_registration_by_params(
            iss, client_id, action=None, request=self._request
        )
        self._registration = registration
        return registration


class InsecureFastAPIMessageLaunch(FastAPIMessageLaunch[InsecureToolConf]):
    """Message launch helper that bypasses platform validation in development."""

    def validate_registration(self):  # type: ignore[override]
        iss = self.get_iss()
        jwt_body = self._get_jwt_body()
        client_id = self.get_client_id() or iss
        self._registration = self._tool_config.find_registration_by_params(
            iss, client_id, action=None, request=self._request, jwt_body=jwt_body
        )
        return self

    def validate_jwt_signature(self):  # type: ignore[override]
        return self

    def validate_deployment(self):  # type: ignore[override]
        return self
