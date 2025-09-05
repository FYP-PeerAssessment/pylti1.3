from typing import Dict, Any, Optional, Union

import fastapi

from pylti1p3.contrib.fastapi.request import FastAPIRequest
from pylti1p3.cookie import CookieService


class FastAPICookieService(CookieService):
    _request: FastAPIRequest
    _cookie_data_to_set: Dict[str, Dict[str, Union[str, int]]]

    def __init__(self, request: FastAPIRequest) -> None:
        self._request = request
        self._cookie_data_to_set = {}

    def _get_key(self, key: str) -> str:
        return self._cookie_prefix + "-" + key

    def get_cookie(self, name: str) -> Optional[str]:
        return self._request.get_cookie(self._get_key(name))

    def set_cookie(self, name: str, value: Union[str, int], exp: int = 3600) -> None:
        self._cookie_data_to_set[self._get_key(name)] = {
            "value": value,
            "exp": exp,
        }

    def update_response(self, response: fastapi.Response) -> None:
        is_secure = self._request.is_secure()
        for key, cookie_data in self._cookie_data_to_set.items():
            cookie_kwargs = {
                "key": key,
                "value": cookie_data["value"],
                "max_age": cookie_data["exp"],
                "secure": is_secure,
                "path": "/",
                "httponly": True,
                "samesite": None,
            }
            if is_secure:
                cookie_kwargs["samesite"] = "None"
            response.set_cookie(**cookie_kwargs)
