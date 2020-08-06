from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class UserSummaryModel:
    """  """

    username: Optional[str] = None
    uuid: Optional[str] = None
    accounts: Optional[List[str]] = None
    projects: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        username = self.username
        uuid = self.uuid
        if self.accounts is None:
            accounts = None
        else:
            accounts = self.accounts

        if self.projects is None:
            projects = None
        else:
            projects = self.projects

        return {
            "username": username,
            "uuid": uuid,
            "accounts": accounts,
            "projects": projects,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> UserSummaryModel:
        username = d.get("username")

        uuid = d.get("uuid")

        accounts = d.get("accounts")

        projects = d.get("projects")

        return UserSummaryModel(username=username, uuid=uuid, accounts=accounts, projects=projects, )
