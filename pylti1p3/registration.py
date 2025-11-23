import typing as t
from collections import abc
from jwcrypto.jwk import JWK


class TKey(t.TypedDict):
    kid: str
    alg: str


class TKeySet(t.TypedDict):
    keys: list[TKey]


class Registration:
    _issuer: str | None = None
    _client_id: str | None = None
    _key_set_url: str | None = None
    _key_set: TKeySet | None = None
    _auth_token_url: str | None = None
    _auth_login_url: str | None = None
    _tool_private_key: str | None = None
    _auth_audience: str | None = None
    _tool_public_key: str | None = None

    def get_issuer(self) -> str | None:
        return self._issuer

    def set_issuer(self, issuer: str) -> "Registration":
        self._issuer = issuer
        return self

    def get_client_id(self) -> str | None:
        return self._client_id

    def set_client_id(self, client_id: str) -> "Registration":
        self._client_id = client_id
        return self

    def get_key_set(self) -> TKeySet | None:
        return self._key_set

    def set_key_set(self, key_set: TKeySet | None) -> "Registration":
        self._key_set = key_set
        return self

    def get_key_set_url(self) -> str | None:
        return self._key_set_url

    def set_key_set_url(self, key_set_url: str | None) -> "Registration":
        self._key_set_url = key_set_url
        return self

    def get_auth_token_url(self) -> str | None:
        return self._auth_token_url

    def set_auth_token_url(self, auth_token_url: str) -> "Registration":
        self._auth_token_url = auth_token_url
        return self

    def get_auth_login_url(self) -> str | None:
        return self._auth_login_url

    def set_auth_login_url(self, auth_login_url: str | None) -> "Registration":
        self._auth_login_url = auth_login_url
        return self

    def get_auth_audience(self) -> str | None:
        return self._auth_audience

    def set_auth_audience(self, auth_audience: str | None) -> "Registration":
        self._auth_audience = auth_audience
        return self

    def get_tool_private_key(self) -> str | None:
        return self._tool_private_key

    def set_tool_private_key(self, tool_private_key: str) -> "Registration":
        self._tool_private_key = tool_private_key
        return self

    def get_tool_public_key(self):
        return self._tool_public_key

    def set_tool_public_key(self, tool_public_key: str | None) -> "Registration":
        self._tool_public_key = tool_public_key
        return self

    @classmethod
    def get_jwk(cls, public_key: str) -> abc.Mapping[str, t.Any]:
        jwk_obj = JWK.from_pem(public_key.encode("utf-8"))
        public_jwk = jwk_obj.export_public(as_dict=True)
        # For LTI 1.3 we always use RS256
        # Prevent this value to be overridden from the key itself
        public_jwk["alg"] = "RS256"
        public_jwk["use"] = "sig"
        return public_jwk

    def get_jwks(self) -> list[abc.Mapping[str, t.Any]]:
        keys: list[abc.Mapping[str, t.Any]] = []
        public_key = self.get_tool_public_key()
        if public_key:
            keys.append(Registration.get_jwk(public_key))
        return keys

    def get_kid(self) -> str | None:
        key = self.get_tool_public_key()
        if key:
            jwk = Registration.get_jwk(key)
            return jwk.get("kid") if jwk else None
        return None
