"""Role parsing helpers used to check launch access grants."""

from abc import ABC
from enum import StrEnum


class RoleType(StrEnum):
    """Canonical LTI role categories encoded in the role URI."""

    SYSTEM = "system"
    INSTITUTION = "institution"
    CONTEXT = "membership"


class AbstractRole(ABC):
    """Parses the JWT role claim and checks for specific access levels."""

    _base_prefix: str = "http://purl.imsglobal.org/vocab/lis/v2"
    _role_types = [RoleType.SYSTEM, RoleType.INSTITUTION, RoleType.CONTEXT]
    _jwt_roles: list[str] = []
    _common_roles: tuple | None = None
    _system_roles: tuple | None = None
    _institution_roles: tuple | None = None
    _context_roles: tuple | None = None

    def __init__(self, jwt_body):
        self._jwt_roles = jwt_body.get("https://purl.imsglobal.org/spec/lti/claim/roles", [])

    def check(self) -> bool:
        roles = [self.parse_role_str(role_str) for role_str in self._jwt_roles]

        context_roles = [
            (role_name, role_type)
            for role_name, role_type in roles
            if role_type == RoleType.CONTEXT
        ]

        if context_roles:
            roles = context_roles

        for role_name, role_type in roles:
            res = self._check_access(role_name, role_type)
            if res:
                return True
        return False

    def _check_access(self, role_name: str, role_type: RoleType | None = None):
        return bool(
            (self._system_roles and role_type == RoleType.SYSTEM and role_name in self._system_roles)
            or (self._institution_roles and role_type == RoleType.INSTITUTION and role_name in self._institution_roles)
            or (self._context_roles and role_type == RoleType.CONTEXT and role_name in self._context_roles)
            or (self._common_roles and role_type is None and role_name in self._common_roles)
        )

    def parse_role_str(self, role_str: str) -> tuple[str, str | None]:
        if role_str.startswith(self._base_prefix):
            role = role_str[len(self._base_prefix) :]
            role_parts = role.split("/")
            role_name_parts = role_parts[-1].split("#")

            if len(role_parts) > 1 and len(role_name_parts) > 1:
                role_type = role_name_parts[0] if role_name_parts[0] == "membership" else role_parts[1]
                role_name = role_name_parts[1]
                if role_type in self._role_types:
                    return role_name, role_type
                return role_name, None
        return role_str, None


class StaffRole(AbstractRole):
    """Matches roles that should be treated as staff access."""

    _system_roles = ("Administrator", "SysAdmin")
    _institution_roles = ("Faculty", "SysAdmin", "Staff", "Instructor")


class StudentRole(AbstractRole):
    """Matches roles that should be treated as student access."""

    _common_roles = ("Learner", "Member", "User")
    _system_roles = ("User",)
    _institution_roles = ("Student", "Learner", "Member", "ProspectiveStudent", "User")
    _context_roles = ("Learner", "Member")


class TeacherRole(AbstractRole):
    """Matches roles that should be treated as instructor access."""

    _common_roles = ("Instructor", "Administrator")
    _context_roles = ("Instructor", "Administrator")


class TeachingAssistantRole(AbstractRole):
    """Matches teaching assistant roles."""

    _context_roles = ("TeachingAssistant",)


class DesignerRole(AbstractRole):
    """Matches content developer roles."""

    _common_roles = ("ContentDeveloper",)
    _context_roles = ("ContentDeveloper",)


class ObserverRole(AbstractRole):
    """Matches mentor or observer roles."""

    _common_roles = ("Mentor",)
    _context_roles = ("Mentor",)


class TransientRole(AbstractRole):
    """Matches transient roles used for temporary participants."""

    _common_roles = ("Transient",)
    _system_roles = ("Transient",)
    _institution_roles = ("Transient",)
    _context_roles = ("Transient",)
