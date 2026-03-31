"""Django implementation of the launch validator."""

from pylti1p3.message_launch import MessageLaunch
from pylti1p3.request import Request
from pylti1p3.service_connector import ServiceConnector
from .cookie import DjangoCookieService
from .request import DjangoRequest
from .service_connector import DjangoServiceConnector
from .session import DjangoSessionService


class DjangoMessageLaunch(MessageLaunch):
    """Wraps Django requests so launch validation can read params and cookies."""

    def __init__(
        self,
        request,
        tool_config,
        session_service=None,
        cookie_service=None,
        launch_data_storage=None,
        requests_session=None,
    ):
        django_request = request if isinstance(request, Request) else DjangoRequest(request, post_only=True)
        cookie_service = cookie_service if cookie_service else DjangoCookieService(django_request)
        session_service = session_service if session_service else DjangoSessionService(request)
        super().__init__(
            django_request,
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
        return DjangoServiceConnector(self._registration, self._requests_session)
