import unittest
from unittest.mock import patch

import requests
import requests_mock

from pylti1p3.cookie import CookieService
from pylti1p3.oidc_login import OIDCLogin
from pylti1p3.redirect import Redirect
from pylti1p3.request import Request
from pylti1p3.session import SessionService
from pylti1p3.service_connector import ServiceConnector
from pylti1p3.utils import add_param_to_url

from .request import FakeRequest
from .tool_config import TOOL_CONFIG, get_test_tool_conf


class TestRequest(Request):
    def __init__(self, request):
        self._request = request

    @property
    def session(self):
        return self._request.session

    def is_secure(self) -> bool:
        return self._request.is_secure()

    def get_param(self, key: str) -> str | None:
        return self._request.GET.get(key, self._request.POST.get(key))


class TestCookieService(CookieService):
    def __init__(self):
        self.cookies: dict[str, str] = {}

    def get_cookie(self, name: str) -> str | None:
        return self.cookies.get(f"{self._cookie_prefix}-{name}")

    def set_cookie(self, name: str, value: str | int, exp: int | None = 3600):
        self.cookies[f"{self._cookie_prefix}-{name}"] = str(value)


class TestRedirect(Redirect[str]):
    def __init__(self, url: str, _cookie_service: TestCookieService):
        self._url = url

    def do_redirect(self) -> str:
        return self._url

    def do_js_redirect(self) -> str:
        return self._url

    def set_redirect_url(self, location: str):
        self._url = location

    def get_redirect_url(self) -> str:
        return self._url


class TestOIDCLogin(OIDCLogin[TestRequest, object, SessionService, TestCookieService, str]):
    def get_redirect(self, url: str) -> Redirect[str]:
        return TestRedirect(url, self._cookie_service)


class TestUtils(unittest.TestCase):
    def test_add_param_to_url(self):
        res = add_param_to_url("https://lms.example.com/class/2923/groups/sets", "user_id", 123)
        self.assertEqual(res, "https://lms.example.com/class/2923/groups/sets?user_id=123")

        res = add_param_to_url("https://lms.example.com/class/2923/groups/sets?some=xxx", "user_id", 123)
        self.assertIn(
            res,
            [
                "https://lms.example.com/class/2923/groups/sets?some=xxx&user_id=123",
                "https://lms.example.com/class/2923/groups/sets?user_id=123&some=xxx",
            ],
        )

        res = add_param_to_url("https://lms.example.com/class/2923/groups/sets?user_id=456", "user_id", 123)
        self.assertEqual(res, "https://lms.example.com/class/2923/groups/sets?user_id=123")

    def test_oidc_login_preserves_existing_auth_query_params(self):
        tool_conf = get_test_tool_conf()
        request = FakeRequest(
            get={
                "iss": "https://canvas.instructure.com",
                "login_hint": "login-hint",
                "target_link_uri": "http://lti.django.test/launch/",
                "lti_message_hint": "message-hint",
            }
        )
        original_auth_login_url = TOOL_CONFIG["https://canvas.instructure.com"]["auth_login_url"]
        TOOL_CONFIG["https://canvas.instructure.com"]["auth_login_url"] = (
            "http://canvas.docker/api/lti/authorize_redirect?existing=1"
        )

        try:
            wrapped_request = TestRequest(request)
            oidc_login = TestOIDCLogin(
                wrapped_request,
                tool_conf,
                session_service=SessionService(wrapped_request),
                cookie_service=TestCookieService(),
            )
            with (
                patch.object(TestOIDCLogin, "_get_uuid", autospec=True, return_value="test-uuid"),
                patch.object(TestOIDCLogin, "_generate_nonce", autospec=True, return_value="test-nonce"),
            ):
                redirect_url = oidc_login.redirect("http://lti.django.test/launch/")
        finally:
            TOOL_CONFIG["https://canvas.instructure.com"]["auth_login_url"] = original_auth_login_url

        self.assertIn("existing=1", redirect_url)
        self.assertIn("state=state-test-uuid", redirect_url)
        self.assertIn("nonce=test-nonce", redirect_url)

    def test_service_connector_keeps_next_page_url_case(self):
        tool_conf = get_test_tool_conf()
        registration = tool_conf.find_registration("https://canvas.instructure.com")
        assert registration is not None
        connector = ServiceConnector(registration)

        with requests_mock.Mocker() as m:
            m.post(
                "http://canvas.docker/login/oauth2/token",
                text='{"access_token": "token"}',
            )
            m.get(
                "http://canvas.docker/api/lti/courses/1/line_items",
                text="[]",
                headers={"Link": '<http://canvas.docker/api/lti/courses/1/line_items?page=ABC123>; rel="next"'},
            )

            response = connector.make_service_request(
                ["https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly"],
                "http://canvas.docker/api/lti/courses/1/line_items",
            )

        self.assertEqual(
            response["next_page_url"],
            "http://canvas.docker/api/lti/courses/1/line_items?page=ABC123",
        )

    def test_service_connector_raises_actionable_exception_message(self):
        tool_conf = get_test_tool_conf()
        registration = tool_conf.find_registration("https://canvas.instructure.com")
        assert registration is not None
        connector = ServiceConnector(registration)

        with requests_mock.Mocker() as m:
            m.post(
                "http://canvas.docker/login/oauth2/token",
                status_code=500,
                text="boom",
            )

            with self.assertRaisesRegex(
                Exception,
                "There was an error while getting an access token from the platform.",
            ):
                connector.get_access_token(
                    ["https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly"]
                )

    def test_service_connector_rejects_non_json_access_token_response(self):
        tool_conf = get_test_tool_conf()
        registration = tool_conf.find_registration("https://canvas.instructure.com")
        assert registration is not None
        connector = ServiceConnector(registration, requests.Session())

        with requests_mock.Mocker() as m:
            m.post(
                "http://canvas.docker/login/oauth2/token",
                text="not-json",
                headers={"Content-Type": "text/plain"},
            )

            with self.assertRaisesRegex(
                Exception,
                "The platform did not return a JSON response for the access token.",
            ):
                connector.get_access_token(
                    ["https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly"]
                )
