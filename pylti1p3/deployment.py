"""Simple deployment identifier holder."""

class Deployment:
    """Represents a platform deployment matched during launch validation."""

    _deployment_id: str | None = None

    def get_deployment_id(self) -> str | None:
        return self._deployment_id

    def set_deployment_id(self, deployment_id: str) -> "Deployment":
        self._deployment_id = deployment_id
        return self
