from typing import Any, Optional

from requests import Session

from pylti1p3.contrib.fastapi.request import FastAPIRequest
from pylti1p3.message_launch import MessageLaunch
from pylti1p3.tool_config import ToolConfAbstract
from pylti1p3.launch_data_storage.base import LaunchDataStorage

from .cookie import FastAPICookieService
from .session import FastAPISessionService


class FastAPIMessageLaunch(MessageLaunch):
    def __init__(
        self,
        request: FastAPIRequest,
        tool_config: ToolConfAbstract,
        session_service: Optional[FastAPISessionService] = None,
        cookie_service: Optional[FastAPICookieService] = None,
        launch_data_storage: Optional[LaunchDataStorage[Any]] = None,
        requests_session: Optional[Session] = None,
    ) -> None:
        cookie_service = (
            cookie_service if cookie_service else FastAPICookieService(request)
        )
        session_service = (
            session_service if session_service else FastAPISessionService(request)
        )
        super().__init__(
            request,
            tool_config,
            session_service,
            cookie_service,
            launch_data_storage,
            requests_session,
        )

    def _get_request_param(self, key: str) -> str:
        return self._request.get_param(key)
