from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, cast

from .storage_type import StorageType


@dataclass
class ProjectModel:
    """  """

    uuid: Optional[str] = None
    name: Optional[str] = None
    account_uuid: Optional[str] = None
    storage_type: Optional[StorageType] = None
    storage_identifier: Optional[str] = None
    external_reference: Optional[str] = None
    users: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        uuid = self.uuid
        name = self.name
        account_uuid = self.account_uuid
        storage_type = self.storage_type.value if self.storage_type else None

        storage_identifier = self.storage_identifier
        external_reference = self.external_reference
        if self.users is None:
            users = None
        else:
            users = self.users

        return {
            "uuid": uuid,
            "name": name,
            "account_uuid": account_uuid,
            "storage_type": storage_type,
            "storage_identifier": storage_identifier,
            "external_reference": external_reference,
            "users": users,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> ProjectModel:
        uuid = d.get("uuid")

        name = d.get("name")

        account_uuid = d.get("account_uuid")

        storage_type = None
        if d.get("storage_type") is not None:
            storage_type = StorageType(d.get("storage_type"))

        storage_identifier = d.get("storage_identifier")

        external_reference = d.get("external_reference")

        users = d.get("users")

        return ProjectModel(
            uuid=uuid,
            name=name,
            account_uuid=account_uuid,
            storage_type=storage_type,
            storage_identifier=storage_identifier,
            external_reference=external_reference,
            users=users,
        )
