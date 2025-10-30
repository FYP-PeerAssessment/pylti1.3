from typing import Any, Optional, override

import fastapi
from fastapi.responses import HTMLResponse

from pylti1p3.oidc_login import OIDCLogin, ToolConfT
from pylti1p3.contrib.fastapi.request import FastAPIRequest
from pylti1p3.launch_data_storage.base import LaunchDataStorage

from .cookie import FastAPICookieService
from .redirect import FastAPIRedirect
from .session import FastAPISessionService


class FastAPIOIDCLogin(
    OIDCLogin[FastAPIRequest, ToolConfT, FastAPISessionService, FastAPICookieService, fastapi.Response]
):
    def __init__(
        self,
        request: FastAPIRequest,
        tool_config: ToolConfT,
        session_service: Optional[FastAPISessionService] = None,
        cookie_service: Optional[FastAPICookieService] = None,
        launch_data_storage: Optional[LaunchDataStorage[Any]] = None,
    ) -> None:
        cookie_service = cookie_service if cookie_service else FastAPICookieService(request)
        session_service = session_service if session_service else FastAPISessionService(request)
        super().__init__(
            request,
            tool_config,
            session_service,
            cookie_service,
            launch_data_storage,
        )

    @override
    def get_redirect(self, url: str) -> FastAPIRedirect:
        return FastAPIRedirect(url, self._cookie_service)

    @override
    def get_response(self, html: str) -> HTMLResponse:
        return HTMLResponse(content=html)
