from __future__ import annotations

from pytailor.common.base import APIBase
from pytailor.clients import RestClient
from pytailor.models import PermissionList, PermissionChange


class Project(APIBase):
    """
    Represents a Tailor project.

    Parameters
    ----------
    project_id : str
        Must be the id of an existing Tailor project
    """

    def __init__(self, project_id: str):
        self.id = project_id
        with RestClient() as client:
            self.__project_model = self._handle_rest_client_call(
                client.get_project,
                self.id,
                error_msg=f"Could not find project with id {project_id}.",
            )
        self.name = self.__project_model.name

    @classmethod
    def from_name(cls, project_name: str) -> Project:
        """Get project with name *project_name*."""
        with RestClient() as client:
            projects = cls._handle_rest_client_call(
                client.get_projects, error_msg=f"Error while fetching projects."
            )
            for prj in projects:
                if project_name == prj.name:
                    return Project(prj.id)
            raise ValueError(f"Could not find project with name {project_name}.")

    def add_workflow_definition(self, workflow_definition_id: str):
        """Add workflow definition with id *workflow_defninition_id* to project."""
        permission_change = PermissionChange(add=[workflow_definition_id])
        with RestClient() as client:
            permission_list: PermissionList = self._handle_rest_client_call(
                client.update_workflow_definitions_for_project,
                self.id,
                permission_change,
                error_msg=f"Error while adding workflow definition to project."
            )
