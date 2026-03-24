"""FastAPI session service adapter."""

from pylti1p3.session import SessionService


class FastAPISessionService(SessionService):
    """Uses the FastAPI request session to store launch state."""

    pass
