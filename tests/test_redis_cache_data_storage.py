from pylti1p3.contrib import RedisCacheDataStorage


class FakeRedis:
    _data = None

    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value, ex=None):  # pylint: disable=unused-argument
        self._data[key] = value

    def exists(self, key):
        return 1 if key in self._data else 0


class TestRedisCacheDataStorage:
    def test_set_and_get_value(self):
        redis = FakeRedis()
        storage = RedisCacheDataStorage(redis)

        storage.set_value("launch", {"state": "state-123", "nonce": "nonce-123"})

        launch_data = storage.get_value("launch")

        assert launch_data == {"state": "state-123", "nonce": "nonce-123"}

    def test_check_value(self):
        redis = FakeRedis()
        storage = RedisCacheDataStorage(redis)

        storage.set_value("state", {"key": "value"})

        assert storage.check_value("state") is True
        assert storage.check_value("missing") is False

    def test_session_prefix(self):
        redis = FakeRedis()
        storage = RedisCacheDataStorage(redis)
        storage.set_session_id("session-123")

        storage.set_value("state", {"key": "value"})

        assert storage.get_value("state") == {"key": "value"}
        assert redis.exists("lti1p3-session-123-state") == 1

    def test_can_set_keys_expiration(self):
        storage = RedisCacheDataStorage(FakeRedis())

        assert storage.can_set_keys_expiration() is True
