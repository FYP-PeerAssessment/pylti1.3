import importlib.util
import pathlib
import sys
import types
import unittest
from datetime import datetime, timedelta

from pylti1p3.service_connector import ServiceConnector

from .tool_config import get_test_tool_conf


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_module(module_name: str, relative_path: str):
    if "pylti1p3.contrib" not in sys.modules:
        contrib_pkg = types.ModuleType("pylti1p3.contrib")
        contrib_pkg.__path__ = [str(ROOT / "pylti1p3" / "contrib")]
        sys.modules["pylti1p3.contrib"] = contrib_pkg

    package_name = module_name.rsplit(".", 1)[0]
    if package_name not in sys.modules:
        package_module = types.ModuleType(package_name)
        package_module.__path__ = [str((ROOT / relative_path).parent)]
        sys.modules[package_name] = package_module

    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestServiceConnectorCache(unittest.TestCase):
    def test_base_connector_caches_per_instance(self):
        tool_conf = get_test_tool_conf()
        registration = tool_conf.find_registration("https://canvas.instructure.com")
        assert registration is not None
        connector = ServiceConnector(registration)

        connector._cache_access_token("scope", "token", 1)  # pylint: disable=protected-access

        self.assertEqual(connector._get_cached_access_token("scope"), "token")  # pylint: disable=protected-access

    def test_flask_connector_reuses_unexpired_tokens(self):
        module = load_module(
            "pylti1p3.contrib.flask.service_connector",
            "pylti1p3/contrib/flask/service_connector.py",
        )
        connector_cls = module.FlaskServiceConnector
        connector_cls.access_tokens = {
            "scope": ("token", datetime.now() + timedelta(seconds=60)),
        }
        tool_conf = get_test_tool_conf()
        registration = tool_conf.find_registration("https://canvas.instructure.com")
        assert registration is not None
        connector = connector_cls(registration)

        self.assertEqual(connector._get_cached_access_token("scope"), "token")  # pylint: disable=protected-access

    def test_fastapi_connector_ignores_expired_tokens(self):
        module = load_module(
            "pylti1p3.contrib.fastapi.service_connector",
            "pylti1p3/contrib/fastapi/service_connector.py",
        )
        connector_cls = module.FastAPIServiceConnector
        connector_cls.access_tokens = {
            "scope": ("token", datetime.now() - timedelta(seconds=1)),
        }
        tool_conf = get_test_tool_conf()
        registration = tool_conf.find_registration("https://canvas.instructure.com")
        assert registration is not None
        connector = connector_cls(registration)

        self.assertIsNone(connector._get_cached_access_token("scope"))  # pylint: disable=protected-access
