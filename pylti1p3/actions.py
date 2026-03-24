"""Action names used to route tool configuration lookups."""

from enum import StrEnum


class Action(StrEnum):
    """Supported configuration lookup contexts."""

    OIDC_LOGIN = "oidc_login"
    MESSAGE_LAUNCH = "message_launch"
