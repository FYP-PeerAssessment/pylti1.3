"""Django application config for the tool-config admin integration."""

from django.apps import AppConfig  # type: ignore


class PyLTI1p3ToolConfig(AppConfig):
    """Registers the Django admin app for tool configuration."""

    name = "pylti1p3.contrib.django.lti1p3_tool_config"
    verbose_name = "PyLTI 1.3 Tool Config"
