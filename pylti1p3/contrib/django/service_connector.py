"""Django-specific access token caching for service requests."""

from math import floor

from django.core.cache import cache  # type: ignore

from pylti1p3.service_connector import ServiceConnector


class DjangoServiceConnector(ServiceConnector):
    def _get_cache_key(self, scope_key: str) -> str:
        return f"lti1p3-access-token-{scope_key}"

    def _get_cached_access_token(self, scope_key: str) -> str | None:
        token = cache.get(self._get_cache_key(scope_key))
        return token if isinstance(token, str) else None

    def _cache_access_token(self, scope_key: str, access_token: str, expires_in: float):
        expires_in = max(1, expires_in - 10)
        cache.set(self._get_cache_key(scope_key), access_token, floor(expires_in))
