"""FastAPI implementation of the launch validator."""

from typing import Any, TypeVar, override

from requests import Session

from pylti1p3.contrib.fastapi.request import FastAPIRequest
from pylti1p3.message_launch import MessageLaunch
from pylti1p3.launch_data_storage.base import LaunchDataStorage
from pylti1p3.service_connector import ServiceConnector
from pylti1p3.tool_config.abstract import ToolConfAbstract

from .cookie import FastAPICookieService
from .service_connector import FastAPIServiceConnector
from .session import FastAPISessionService

ToolConfT = TypeVar("ToolConfT", bound=ToolConfAbstract)


class FastAPIMessageLaunch(MessageLaunch[FastAPIRequest, ToolConfT, FastAPISessionService, FastAPICookieService]):
    """Wraps a FastAPI request so launch validation can read params and cookies."""

    def __init__(
        self,
        request: FastAPIRequest,
        tool_config: ToolConfT,
        session_service: FastAPISessionService | None = None,
        cookie_service: FastAPICookieService | None = None,
        launch_data_storage: LaunchDataStorage[Any] | None = None,
        requests_session: Session | None = None,
    ) -> None:
        cookie_service = cookie_service if cookie_service else FastAPICookieService(request)
        session_service = session_service if session_service else FastAPISessionService(request)
        super().__init__(
            request,
            tool_config,
            session_service,
            cookie_service,
            launch_data_storage,
            requests_session,
        )

    @override
    def _get_request_param(self, key: str) -> str:
        val = self._request.get_param(key)
        if val is not None:
            return val
        raise ValueError(f"Missing request param: {key}")

    @override
    def get_service_connector(self) -> ServiceConnector:
        assert self._registration is not None, "Registration not yet set"
        return FastAPIServiceConnector(self._registration, self._requests_session)
