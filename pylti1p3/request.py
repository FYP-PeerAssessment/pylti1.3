"""Abstract request wrapper used to read launch parameters and cookies."""

from abc import ABC, abstractmethod


class Request(ABC):
    """Unifies request access across Flask, Django, and FastAPI adapters."""

    @property
    def session(self):
        raise NotImplementedError

    @abstractmethod
    def is_secure(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_param(self, key: str) -> str:
        raise NotImplementedError
