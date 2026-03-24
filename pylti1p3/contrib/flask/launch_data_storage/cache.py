"""Flask cache implementation for launch storage."""

from pylti1p3.launch_data_storage.cache import CacheDataStorage


class FlaskCacheDataStorage(CacheDataStorage):
    """Uses Flask-compatible cache storage for launch data."""

    _cache = None

    def __init__(self, cache, **kwargs):
        self._cache = cache
        super().__init__(cache, **kwargs)
