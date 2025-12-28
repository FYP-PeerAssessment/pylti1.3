from typing import Any

import fastapi  # type: ignore
import starlette.datastructures  # type: ignore

from pylti1p3.request import Request


class FastAPIRequest(Request):
    _request: fastapi.Request
    _form_data: starlette.datastructures.FormData

    def __init__(self, request: fastapi.Request, form_data: starlette.datastructures.FormData) -> None:
        """
        Parameters:
            request: FastAPI request
            form_data: form data from FastAPI request
                To get form data from FastAPI request, must use async method.
                As we don't use async functions here, form data must be provided from outside.
        """

        super().__init__()

        self._request = request
        self._form_data = form_data

    @property
    def session(self) -> dict[str, Any]:
        return self._request.session

    def get_param(self, key: str) -> str | None:
        if self._request.method == "GET":
            return self._request.query_params.get(key, None)
        return self._form_data.get(key)

    def get_cookie(self, key: str) -> str | None:
        return self._request.cookies.get(key, None)

    def is_secure(self) -> bool:
        return self._request.url.is_secure
