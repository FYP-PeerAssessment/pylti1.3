"""Flask implementation of the launch validator."""

from pylti1p3.message_launch import MessageLaunch
from pylti1p3.service_connector import ServiceConnector
from .cookie import FlaskCookieService
from .service_connector import FlaskServiceConnector
from .session import FlaskSessionService


class FlaskMessageLaunch(MessageLaunch):
    """Wraps a Flask request so launch validation can read params and cookies."""

    def __init__(
        self,
        request,
        tool_config,
        session_service=None,
        cookie_service=None,
        launch_data_storage=None,
        requests_session=None,
    ):
        cookie_service = cookie_service if cookie_service else FlaskCookieService(request)
        session_service = session_service if session_service else FlaskSessionService(request)
        super().__init__(
            request,
            tool_config,
            session_service,
            cookie_service,
            launch_data_storage,
            requests_session,
        )

    def _get_request_param(self, key):
        return self._request.get_param(key)

    def get_service_connector(self) -> ServiceConnector:
        assert self._registration is not None, "Registration not yet set"
        return FlaskServiceConnector(self._registration, self._requests_session)
