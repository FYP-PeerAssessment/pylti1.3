import json
from unittest.mock import patch

import requests_mock

from .base import TestServicesBase
from .request import FakeRequest
from .tool_config import get_test_tool_conf


class TestPlatformNotificationService(TestServicesBase):
    def _get_jwt_body_with_pns(self):
        jwt_body = self._get_jwt_body().copy()
        jwt_body["https://purl.imsglobal.org/spec/lti/claim/platformnotificationservice"] = {
            "service_versions": ["1.0"],
            "platform_notification_service_url": "http://canvas.docker/api/lti/notice-handlers/1",
            "scope": ["https://purl.imsglobal.org/spec/lti/scope/noticehandlers"],
            "notice_types_supported": [
                "LtiHelloWorldNotice",
                "LtiContextCopyNotice",
            ],
        }
        return jwt_body

    def test_register_and_get_notice_handlers(self):
        # pylint: disable=import-outside-toplevel
        from pylti1p3.contrib.flask import FlaskMessageLaunch

        tool_conf = get_test_tool_conf()
        notice_service_url = "http://canvas.docker/api/lti/notice-handlers/1"

        with patch.object(FlaskMessageLaunch, "_get_jwt_body", autospec=True) as get_jwt_body:
            message_launch = FlaskMessageLaunch(FakeRequest(), tool_conf)
            get_jwt_body.side_effect = lambda x: self._get_jwt_body_with_pns()

            with patch("socket.gethostbyname", return_value="127.0.0.1"):
                with requests_mock.Mocker() as m:
                    m.post(
                        self._get_auth_token_url(),
                        text=json.dumps(self._get_auth_token_response()),
                    )

                    m.put(
                        notice_service_url,
                        text=json.dumps(
                            {
                                "notice_type": "LtiContextCopyNotice",
                                "handler": "https://tool.example.com/notice_handlers/1",
                            }
                        ),
                    )
                    m.get(
                        notice_service_url,
                        text=json.dumps(
                            {
                                "client_id": 10000000000068,
                                "deployment_id": "106:abc",
                                "notice_handlers": [
                                    {
                                        "notice_type": "LtiContextCopyNotice",
                                        "handler": "https://tool.example.com/notice_handlers/1",
                                    }
                                ],
                            }
                        ),
                    )

                    pns = message_launch.validate_registration().get_pns()
                    self.assertEqual(
                        pns.get_supported_notice_types(),
                        ["LtiHelloWorldNotice", "LtiContextCopyNotice"],
                    )

                    register_response = pns.register_notice_handler(
                        "LtiContextCopyNotice",
                        "https://tool.example.com/notice_handlers/1",
                    )
                    self.assertEqual(
                        register_response["body"],
                        {
                            "notice_type": "LtiContextCopyNotice",
                            "handler": "https://tool.example.com/notice_handlers/1",
                        },
                    )

                    handlers_response = pns.get_notice_handlers()
                    self.assertEqual(handlers_response["body"]["client_id"], 10000000000068)
                    self.assertEqual(len(handlers_response["body"]["notice_handlers"]), 1)

    def test_has_pns(self):
        # pylint: disable=import-outside-toplevel
        from pylti1p3.contrib.flask import FlaskMessageLaunch

        tool_conf = get_test_tool_conf()

        with patch.object(FlaskMessageLaunch, "_get_jwt_body", autospec=True) as get_jwt_body:
            message_launch = FlaskMessageLaunch(FakeRequest(), tool_conf)
            get_jwt_body.side_effect = lambda x: self._get_jwt_body_with_pns()
            self.assertTrue(message_launch.has_pns())

            get_jwt_body.side_effect = lambda x: self._get_jwt_body()
            self.assertFalse(message_launch.has_pns())

    def test_get_notice_jwts_from_payload(self):
        # pylint: disable=import-outside-toplevel
        from pylti1p3.platform_notification import PlatformNotificationService

        payload = {
            "notices": [
                {"jwt": "header.payload.signature"},
                {"jwt": "header.payload2.signature2"},
            ]
        }
        self.assertEqual(
            PlatformNotificationService.get_notice_jwts(payload),
            ["header.payload.signature", "header.payload2.signature2"],
        )
