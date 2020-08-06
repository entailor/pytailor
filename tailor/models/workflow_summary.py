from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class WorkflowSummaryModel:
    """  """

    id: Optional[str] = None
    name: Optional[str] = None
    project_uuid: Optional[str] = None
    updated_utc: Optional[str] = None
    user_uuid: Optional[str] = None
    state: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        project_uuid = self.project_uuid
        updated_utc = self.updated_utc
        user_uuid = self.user_uuid
        state = self.state

        return {
            "id": id,
            "name": name,
            "project_uuid": project_uuid,
            "updated_utc": updated_utc,
            "user_uuid": user_uuid,
            "state": state,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> WorkflowSummaryModel:
        id = d.get("id")

        name = d.get("name")

        project_uuid = d.get("project_uuid")

        updated_utc = d.get("updated_utc")

        user_uuid = d.get("user_uuid")

        state = d.get("state")

        return WorkflowSummaryModel(
            id=id, name=name, project_uuid=project_uuid, updated_utc=updated_utc,
            user_uuid=user_uuid, state=state,
        )
