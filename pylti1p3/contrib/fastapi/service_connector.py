"""FastAPI-specific access token caching for service requests."""

from datetime import datetime, timedelta

from pylti1p3.service_connector import ServiceConnector


class FastAPIServiceConnector(ServiceConnector):
    access_tokens: dict[str, tuple[str, datetime]] = {}

    def _get_cached_access_token(self, scope_key: str) -> str | None:
        cached_token = self.__class__.access_tokens.get(scope_key)
        if cached_token is None:
            return None

        token, expires_at = cached_token
        if expires_at > datetime.now():
            return token
        return None

    def _cache_access_token(self, scope_key: str, access_token: str, expires_in: float):
        self.__class__.access_tokens[scope_key] = (
            access_token,
            datetime.now() + timedelta(seconds=expires_in),
        )
