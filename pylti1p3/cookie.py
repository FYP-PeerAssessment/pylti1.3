from abc import ABC, abstractmethod


class CookieService(ABC):
    _cookie_prefix: str = "lti1p3"

    @abstractmethod
    def get_cookie(self, name: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def set_cookie(
        self, name: str, value: str | int, exp: int | None = 3600
    ):
        raise NotImplementedError
