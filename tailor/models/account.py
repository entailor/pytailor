from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AccountModel:
    """  """

    uuid: Optional[str] = None
    organization_name: Optional[str] = None
    organization_id: Optional[str] = None
    projects: Optional[List[str]] = None
    users: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        uuid = self.uuid
        organization_name = self.organization_name
        organization_id = self.organization_id
        if self.projects is None:
            projects = None
        else:
            projects = self.projects

        if self.users is None:
            users = None
        else:
            users = self.users

        return {
            "uuid": uuid,
            "organization_name": organization_name,
            "organization_id": organization_id,
            "projects": projects,
            "users": users,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> AccountModel:
        uuid = d.get("uuid")

        organization_name = d.get("organization_name")

        organization_id = d.get("organization_id")

        projects = d.get("projects")

        users = d.get("users")

        return AccountModel(
            uuid=uuid,
            organization_name=organization_name,
            organization_id=organization_id,
            projects=projects,
            users=users,
        )
