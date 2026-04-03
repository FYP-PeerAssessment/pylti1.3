"""Platform Notification Service helpers for notice-handler registration and delivery payloads."""

import json
import typing as t
import typing_extensions as te

from .service_connector import ServiceConnector, TServiceConnectorResponse


class TPlatformNotificationServiceData(t.TypedDict, total=False):
    """Platform Notification Service metadata from the launch JWT."""

    service_versions: te.Required[list[str]]
    platform_notification_service_url: te.Required[str]
    scope: te.Required[list[t.Literal["https://purl.imsglobal.org/spec/lti/scope/noticehandlers"]]]
    notice_types_supported: list[str]


class TNoticeHandler(t.TypedDict):
    """Single notice-handler record used for registration/list responses."""

    notice_type: str
    handler: str


class TNoticeHandlersResponse(t.TypedDict, total=False):
    """Notice-handler listing response from the platform endpoint."""

    client_id: str | int
    deployment_id: str
    notice_handlers: list[TNoticeHandler]


class TNoticeDeliveryItem(t.TypedDict):
    """Single JWT notice item delivered to the tool's webhook."""

    jwt: str


class TNoticeDeliveryPayload(t.TypedDict):
    """Webhook payload posted by the platform notification service."""

    notices: list[TNoticeDeliveryItem]


class PlatformNotificationService:
    """Registers and lists platform notice handlers for a launch context."""

    _service_connector: ServiceConnector
    _service_data: TPlatformNotificationServiceData

    def __init__(
        self,
        service_connector: ServiceConnector,
        service_data: TPlatformNotificationServiceData,
    ):
        self._service_connector = service_connector
        self._service_data = service_data

    def get_supported_notice_types(self) -> list[str]:
        return self._service_data.get("notice_types_supported", [])

    def get_notice_handlers(self) -> TServiceConnectorResponse:
        return self._service_connector.make_service_request(
            self._service_data["scope"],
            self._service_data["platform_notification_service_url"],
            method="GET",
        )

    def register_notice_handler(self, notice_type: str, handler: str) -> TServiceConnectorResponse:
        data = json.dumps(
            {
                "notice_type": notice_type,
                "handler": handler,
            }
        )

        return self._service_connector.make_service_request(
            self._service_data["scope"],
            self._service_data["platform_notification_service_url"],
            method="PUT",
            data=data,
            content_type="application/json",
            accept="application/json",
        )

    def remove_notice_handler(self, notice_type: str) -> TServiceConnectorResponse:
        return self.register_notice_handler(notice_type, "")

    @staticmethod
    def get_notice_jwts(payload: TNoticeDeliveryPayload) -> list[str]:
        return [notice.get("jwt", "") for notice in payload.get("notices", []) if notice.get("jwt")]
