"""Django session service adapter."""

from pylti1p3.session import SessionService


class DjangoSessionService(SessionService):
    """Uses Django's request session to store launch state."""

    pass
