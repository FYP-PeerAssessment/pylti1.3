from typing import Any

from pylti1p3.launch_data_storage.cache import CacheDataStorage


class FastAPICacheDataStorage(CacheDataStorage):
    _cache: Any

    def __init__(self, cache: Any, **kwargs: Any) -> None:
        self._cache = cache
        super().__init__(cache, **kwargs)
