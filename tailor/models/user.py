from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, cast

from .account import AccountModel
from .project import ProjectModel


@dataclass
class UserModel:
    """  """

    username: Optional[str] = None
    uuid: Optional[str] = None
    accounts: Optional[List[AccountModel]] = None
    projects: Optional[List[ProjectModel]] = None
    name: Optional[str] = None
    email: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        username = self.username
        uuid = self.uuid
        if self.accounts is None:
            accounts = None
        else:
            accounts = []
            for accounts_item_data in self.accounts:
                accounts_item = accounts_item_data.to_dict()

                accounts.append(accounts_item)

        if self.projects is None:
            projects = None
        else:
            projects = []
            for projects_item_data in self.projects:
                projects_item = projects_item_data.to_dict()

                projects.append(projects_item)

        name = self.name
        email = self.email

        return {
            "username": username,
            "uuid": uuid,
            "accounts": accounts,
            "projects": projects,
            "name": name,
            "email": email,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> UserModel:
        username = d.get("username")

        uuid = d.get("uuid")

        accounts = []
        for accounts_item_data in d.get("accounts") or []:
            accounts_item = AccountModel.from_dict(accounts_item_data)

            accounts.append(accounts_item)

        projects = []
        for projects_item_data in d.get("projects") or []:
            projects_item = ProjectModel.from_dict(projects_item_data)

            projects.append(projects_item)

        name = d.get("name")

        email = d.get("email")

        return UserModel(username=username, uuid=uuid, accounts=accounts, projects=projects, name=name, email=email, )
