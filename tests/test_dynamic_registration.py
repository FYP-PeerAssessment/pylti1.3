import json
import unittest
from unittest.mock import Mock

from pylti1p3.dynamic_registration import DynamicRegistration, generate_key_pair
from pylti1p3.exception import LtiException, LtiServiceException


class FakeSession:
    def __init__(self, get_response=None, post_response=None):
        self.get_response = get_response
        self.post_response = post_response
        self.post_calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, _url):
        return self.get_response

    def post(self, url, headers=None, json=None):
        self.post_calls.append((url, headers, json))
        return self.post_response


class TestDynamicRegistration(DynamicRegistration):
    client_name = "Tool"
    description = "Tool description"

    def __init__(self, openid_configuration_endpoint="https://platform.example/openid", registration_token=None):
        self._openid_configuration_endpoint = openid_configuration_endpoint
        self._registration_token = registration_token
        self.completed_with = None
        self._session = None

    def set_session(self, session):
        self._session = session

    def get_request_session(self):
        assert self._session is not None
        return self._session

    def get_initiate_login_uri(self) -> str:
        return "https://tool.example/login"

    def get_jwks_uri(self) -> str:
        return "https://tool.example/jwks"

    def get_redirect_uris(self) -> list[str]:
        return ["https://tool.example/launch"]

    def get_scopes(self) -> list[str]:
        return ["scope-1", "scope-2"]

    def get_domain(self) -> str:
        return "tool.example"

    def get_target_link_uri(self) -> str:
        return "https://tool.example/launch"

    def get_messages(self) -> list[dict[str, str]]:
        return [{"type": "LtiResourceLinkRequest", "target_link_uri": "https://tool.example/launch"}]

    def get_logo_uri(self) -> str:
        return "https://tool.example/logo.png"

    def get_openid_configuration_endpoint(self) -> str:
        return self._openid_configuration_endpoint

    def get_registration_token(self) -> str | None:
        return self._registration_token

    def complete_registration(self, openid_configuration, openid_registration):
        self.completed_with = (openid_configuration, openid_registration)
        return {"saved": True, "client_id": openid_registration["client_id"]}


class TestDynamicRegistrationFlow(unittest.TestCase):
    def test_generate_key_pair_returns_pem_strings(self):
        private_key, public_key = generate_key_pair(2048)

        self.assertTrue(private_key.startswith("-----BEGIN RSA PRIVATE KEY-----"))
        self.assertTrue(public_key.startswith("-----BEGIN PUBLIC KEY-----"))

    def test_register_posts_registration_data_and_returns_completed_value(self):
        openid_configuration = {
            "registration_endpoint": "https://platform.example/register",
            "https://purl.imsglobal.org/spec/lti-platform-configuration": {},
        }
        openid_registration = {
            "client_id": "client-123",
            "https://purl.imsglobal.org/spec/lti-tool-configuration": {},
        }
        registration = TestDynamicRegistration(registration_token="secret-token")
        session = FakeSession(
            get_response=Mock(ok=True, json=Mock(return_value=openid_configuration)),
            post_response=Mock(ok=True, json=Mock(return_value=openid_registration)),
        )
        registration.set_session(session)

        result = registration.register()

        self.assertEqual(result, {"saved": True, "client_id": "client-123"})
        self.assertEqual(session.post_calls[0][0], "https://platform.example/register")
        self.assertEqual(session.post_calls[0][1]["Authorization"], "Bearer secret-token")
        self.assertEqual(session.post_calls[0][2]["client_name"], "Tool")

    def test_register_requires_openid_configuration_endpoint(self):
        registration = TestDynamicRegistration(openid_configuration_endpoint="")
        registration.set_session(FakeSession())

        with self.assertRaisesRegex(LtiException, "No OpenID configuration endpoint was specified."):
            registration.register()

    def test_register_raises_when_registration_response_is_not_json(self):
        openid_configuration = {
            "registration_endpoint": "https://platform.example/register",
            "https://purl.imsglobal.org/spec/lti-platform-configuration": {},
        }
        non_json_response = Mock(ok=True)
        non_json_response.json.side_effect = json.JSONDecodeError("bad json", "doc", 0)
        registration = TestDynamicRegistration()
        registration.set_session(
            FakeSession(
                get_response=Mock(ok=True, json=Mock(return_value=openid_configuration)),
                post_response=non_json_response,
            )
        )

        with self.assertRaisesRegex(LtiServiceException, "The registration endpoint did not return a JSON object."):
            registration.register()
