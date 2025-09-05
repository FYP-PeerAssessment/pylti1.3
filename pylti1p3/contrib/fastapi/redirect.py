from typing import Optional, Union, TypeVar

import fastapi
from fastapi.responses import HTMLResponse, RedirectResponse

from pylti1p3.redirect import Redirect
from pylti1p3.contrib.fastapi.cookie import FastAPICookieService


ResponseT = TypeVar("ResponseT", bound=fastapi.Response)


class FastAPIRedirect(Redirect):
    _location: Optional[str]
    _cookie_service: Optional[FastAPICookieService]

    def __init__(self, location: str, cookie_service: Optional[FastAPICookieService] = None) -> None:
        super().__init__()
        self._location = location
        self._cookie_service = cookie_service

    def do_redirect(self) -> RedirectResponse:
        return self._process_response(RedirectResponse(self._location, status_code=302))

    def do_js_redirect(self) -> HTMLResponse:
        return self._process_response(
            HTMLResponse(
                f'<script type="text/javascript">window.location="{self._location}";</script>'
            )
        )

    def set_redirect_url(self, location: str) -> None:
        self._location = location

    def get_redirect_url(self) -> Optional[str]:
        return self._location

    def _process_response(self, response: ResponseT) -> ResponseT:
        if self._cookie_service:
            self._cookie_service.update_response(response)
        return response
