"""Abstract cookie storage used by framework adapters."""

from abc import ABC, abstractmethod


class CookieService(ABC):
    """Stores and retrieves LTI state cookies for a specific web framework."""

    _cookie_prefix: str = "lti1p3"

    @abstractmethod
    def get_cookie(self, name: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def set_cookie(self, name: str, value: str | int, exp: int | None = 3600):
        raise NotImplementedError
