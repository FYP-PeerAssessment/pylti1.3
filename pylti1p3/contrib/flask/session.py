"""Flask session service adapter."""

from pylti1p3.session import SessionService


class FlaskSessionService(SessionService):
    """Uses Flask's session to store launch state."""

    pass
