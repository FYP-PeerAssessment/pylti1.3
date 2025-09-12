from abc import ABC, abstractmethod


class Request(ABC):
    @property
    def session(self):
        raise NotImplementedError

    @abstractmethod
    def is_secure(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_param(self, key: str) -> str:
        raise NotImplementedError
