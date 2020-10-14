from __future__ import annotations

from typing import List

import httpx
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
            self.__project_model = self._handle_request(
                client.get_project,
                self.id,
                error_msg=f"Could not find project with id {project_id}.",
            )
        self.name = self.__project_model.name

    @classmethod
    def from_name(cls, project_name: str) -> Project:
        """Get project with name *project_name*."""
        with RestClient() as client:
            projects = cls._handle_request(
                client.get_projects, error_msg=f"Error while fetching projects."
            )
            for prj in projects:
                if project_name == prj.name:
                    return Project(prj.id)
            raise ValueError(f"Could not find project with name {project_name}.")

    @classmethod
    def list_projects_names(cls) -> List[str]:
        with RestClient() as client:
            projects = cls._handle_request(
                client.get_projects, error_msg=f"Error while fetching projects."
            )
            return [prj.name for prj in projects]

    def add_workflow_definition(self, workflow_definition_id: str) -> List[str]:
        """Add workflow definition with id *workflow_defninition_id* to project."""
        permission_change = PermissionChange(add=[workflow_definition_id])
        with RestClient() as client:
            permission_list: PermissionList = self._handle_request(
                client.update_workflow_definitions_for_project,
                self.id,
                permission_change,
                error_msg=f"Error while adding workflow definition to project.",
            )
        return permission_list.__root__

    def remove_workflow_definition(self, workflow_definition_id: str) -> List[str]:
        """Remove workflow definition with id *workflow_defninition_id* from project."""
        permission_change = PermissionChange(delete=[workflow_definition_id])
        with RestClient() as client:
            permission_list: PermissionList = self._handle_request(
                client.update_workflow_definitions_for_project,
                self.id,
                permission_change,
                error_msg=f"Error while removing workflow definition to project.",
            )
        return permission_list.__root__

    def list_available_workflow_definitions(self) -> List[dict]:
        """
        Retrieve a list of all available workflow definitions as summary dicts.
        """
        with RestClient() as client:
            wf_def_models = self._handle_request(
                client.get_workflow_definition_summaries_project,
                self.id,
                error_msg="Could not retrieve workflow definition summaries.",
            )
        return [wf_def_model.dict() for wf_def_model in wf_def_models]

    def list_workflows(self) -> List[dict]:
        """
        Retrieve a list of all available workflows as summary dicts.
        """
        with RestClient() as client:
            wf_models = self._handle_request(
                client.get_workflows,
                self.id,
                error_msg="Could not retrieve workflows.",
            )
        return [wf_model.dict() for wf_model in wf_models]

    def delete_workflow(self, workflow_id: str) -> str:
        """
        Delete a workflow and corresponding files by workflow id
        """
        with RestClient() as client:
            response = self._handle_request(
                client.delete_workflow,
                self.id,
                workflow_id,
                error_msg="Could not delete workflow.",
                return_none_on=[httpx.codes.NOT_FOUND]
            )
            if response is None:
                return f'Could not delete workflow {workflow_id}'
        return f'Deleted workflow {workflow_id}'
