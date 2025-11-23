import json
import typing as t
from collections import abc

from pylti1p3.actions import Action
from pylti1p3.deployment import Deployment
from pylti1p3.exception import LtiException
from pylti1p3.registration import Registration
from pylti1p3.request import Request
from pylti1p3.tool_config.abstract import ToolConfAbstract

if t.TYPE_CHECKING:
    from .models import LtiTool, LtiToolKey

default_app_config = "pylti1p3.contrib.django.lti1p3_tool_config.apps.PyLTI1p3ToolConfig"


class DjangoDbToolConf(ToolConfAbstract):
    _lti_tools: dict[str, dict[str, "LtiTool"] | "LtiTool"]
    _tools_cls: type["LtiTool"]
    _keys_cls: type["LtiToolKey"]

    def __init__(self):
        # pylint: disable=import-outside-toplevel
        from .models import LtiTool, LtiToolKey

        super().__init__()
        self._lti_tools = {}
        self._tools_cls = LtiTool
        self._keys_cls = LtiToolKey

    @t.overload
    def get_lti_tool(self, iss: str, client_id: str) -> "LtiTool": ...

    @t.overload
    def get_lti_tool(self, iss: str, client_id: None) -> "dict[str, LtiTool] | LtiTool": ...

    def get_lti_tool(self, iss: str, client_id: str | None):
        # pylint: disable=no-member
        lti_tool: "dict[str, LtiTool] | LtiTool | None" = self._lti_tools.get(iss) if client_id is None else t.cast("LtiTool | None", self._lti_tools.get(iss, {}).get(client_id))
        if lti_tool:
            return lti_tool

        if client_id is None:
            lti_tool = self._tools_cls.objects.filter(issuer=iss, is_active=True).order_by("use_by_default").first()
        else:
            try:
                lti_tool = self._tools_cls.objects.get(issuer=iss, client_id=client_id, is_active=True)
            except self._tools_cls.DoesNotExist:
                pass

        if lti_tool is None:
            raise LtiException(f"iss {iss} [client_id={client_id}] not found in settings")

        if client_id is None:
            self._lti_tools[iss] = lti_tool
        else:
            if iss not in self._lti_tools:
                self._lti_tools[iss] = {}
            self._lti_tools[iss][client_id] = lti_tool  # pyright: ignore

        return lti_tool

    @t.override
    def check_iss_has_one_client(self, iss: str) -> t.Literal[False]:
        return False

    @t.override
    def check_iss_has_many_clients(self, iss: str) -> t.Literal[True]:
        return True

    @t.override
    def find_registration_by_issuer(
        self,
        iss: str,
        *,
        action: Action | None = None,
        request: Request | None = None,
        jwt_body: abc.Mapping[str, t.Any] | None = None,
    ) -> Registration:
        raise NotImplementedError

    @t.override
    def find_registration_by_params(
        self,
        iss: str,
        client_id: str,
        *,
        action: Action | None = None,
        request: Request | None = None,
        jwt_body: abc.Mapping[str, t.Any] | None = None,
    ) -> Registration:
        lti_tool = self.get_lti_tool(iss, client_id)
        if isinstance(lti_tool, dict):
            raise LtiException(f"iss {iss} has many client_ids, please provide client_id to find registration")
        auth_audience = lti_tool.auth_audience if lti_tool.auth_audience else None
        key_set = json.loads(lti_tool.key_set) if lti_tool.key_set else None
        key_set_url = lti_tool.key_set_url if lti_tool.key_set_url else None
        tool_public_key = lti_tool.tool_key.public_key if lti_tool.tool_key.public_key else None

        reg = Registration()
        reg.set_auth_login_url(lti_tool.auth_login_url).set_auth_token_url(lti_tool.auth_token_url).set_auth_audience(
            auth_audience
        ).set_client_id(lti_tool.client_id).set_key_set(key_set).set_key_set_url(key_set_url).set_issuer(
            lti_tool.issuer
        ).set_tool_private_key(lti_tool.tool_key.private_key).set_tool_public_key(tool_public_key)
        return reg

    @t.override
    def find_deployment(self, iss: str, deployment_id: str) -> t.Never:
        raise NotImplementedError

    @t.override
    def find_deployment_by_params(self, iss: str, deployment_id: str, client_id: str | None):
        lti_tool = self.get_lti_tool(iss, client_id)
        if isinstance(lti_tool, dict):
            raise LtiException(f"iss {iss} has many client_ids, please provide client_id to find deployment")
        deployment_ids: list[str] = json.loads(lti_tool.deployment_ids) if lti_tool.deployment_ids else []
        if deployment_id not in deployment_ids:
            return None
        d = Deployment()
        return d.set_deployment_id(deployment_id)

    @t.override
    def get_jwks(self, iss: str | None = None, client_id: str | None = None, **kwargs: t.Any) -> dict[t.Literal['keys'], list[abc.Mapping[str, t.Any]]]:
        # pylint: disable=no-member
        search_kwargs = {}
        if iss:
            search_kwargs["lti_tools__issuer"] = iss
        if client_id:
            search_kwargs["lti_tools__client_id"] = client_id

        assert self._keys_cls is not None
        if search_kwargs:
            search_kwargs["lti_tools__is_active"] = True
            qs = self._keys_cls.objects.filter(**search_kwargs)
        else:
            qs = self._keys_cls.objects.all()

        jwks = []
        public_key_lst = []

        for key in qs:
            if key.public_key and key.public_key not in public_key_lst:
                if key.public_jwk:
                    jwks.append(json.loads(key.public_jwk))
                else:
                    jwks.append(Registration.get_jwk(key.public_key))
                public_key_lst.append(key.public_key)
        return {"keys": jwks}
