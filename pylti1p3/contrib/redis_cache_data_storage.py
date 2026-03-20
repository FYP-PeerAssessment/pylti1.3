import json
import typing as t

from pylti1p3.launch_data_storage.base import LaunchDataStorage

T = t.TypeVar("T")


class RedisCacheDataStorage(LaunchDataStorage[T], t.Generic[T]):
    _redis: t.Any = None

    def __init__(self, redis_client: t.Any, **kwargs: t.Any) -> None:
        self._redis = redis_client
        super().__init__(**kwargs)

    def _get_redis(self) -> t.Any:
        assert self._redis is not None, "Redis client is not set"
        return self._redis

    def get_value(self, key: str) -> T:
        key = self._prepare_key(key)
        value = self._get_redis().get(key)
        if value is None:
            return t.cast(T, None)
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if isinstance(value, str):
            return t.cast(T, json.loads(value))
        return t.cast(T, value)

    def set_value(self, key: str, value: T, exp: int | None = None) -> None:
        key = self._prepare_key(key)
        payload = json.dumps(value)
        self._get_redis().set(key, payload, ex=exp)

    def check_value(self, key: str) -> bool:
        key = self._prepare_key(key)
        return self._get_redis().exists(key) == 1

    def can_set_keys_expiration(self) -> bool:
        return True
