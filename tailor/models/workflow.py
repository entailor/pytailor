from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowModel:
    """  """

    id: Optional[str] = None
    name: Optional[str] = None
    project_uuid: Optional[str] = None
    updated_utc: Optional[str] = None
    user_uuid: Optional[str] = None
    state: Optional[str] = None
    created_utc: Optional[str] = None
    task_links: Optional[Dict[Any, Any]] = None
    root_tasks: Optional[List[int]] = None
    task_states: Optional[Dict[Any, Any]] = None
    file_list: Optional[List[Dict[Any, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        project_uuid = self.project_uuid
        updated_utc = self.updated_utc
        user_uuid = self.user_uuid
        state = self.state
        created_utc = self.created_utc
        task_links = self.task_links
        if self.root_tasks is None:
            root_tasks = None
        else:
            root_tasks = self.root_tasks

        task_states = self.task_states
        if self.file_list is None:
            file_list = None
        else:
            file_list = self.file_list

        return {
            "id": id,
            "name": name,
            "project_uuid": project_uuid,
            "updated_utc": updated_utc,
            "user_uuid": user_uuid,
            "state": state,
            "created_utc": created_utc,
            "task_links": task_links,
            "root_tasks": root_tasks,
            "task_states": task_states,
            "file_list": file_list,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> WorkflowModel:
        id = d.get("id")

        name = d.get("name")

        project_uuid = d.get("project_uuid")

        updated_utc = d.get("updated_utc")

        user_uuid = d.get("user_uuid")

        state = d.get("state")

        created_utc = d.get("created_utc")

        task_links = d.get("task_links")

        root_tasks = d.get("root_tasks")

        task_states = d.get("task_states")

        file_list = d.get("file_list")

        return WorkflowModel(
            id=id,
            name=name,
            project_uuid=project_uuid,
            updated_utc=updated_utc,
            user_uuid=user_uuid,
            state=state,
            created_utc=created_utc,
            task_links=task_links,
            root_tasks=root_tasks,
            task_states=task_states,
            file_list=file_list,
        )
