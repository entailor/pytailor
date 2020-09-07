from __future__ import annotations

from typing import Optional, List

from tailor.clients import RestClient
from tailor.common.base import APIBase
from tailor.exceptions import ExistsBackendError
from tailor.models import WorkflowDefinition as WorkflowDefinitionModel
from tailor.models import WorkflowDefinitionCreate
from tailor.utils import dict_keys_str_to_int, dict_keys_int_to_str
from .account import Account
from .dag import DAG
from .project import Project


class WorkflowDefinition(APIBase):

    def __init__(self,
                 name: str,
                 description: str,
                 dag: DAG,
                 inputs_schema: Optional[dict] = None,
                 outputs_schema: Optional[dict] = None,
                 files_schema: Optional[dict] = None
                 ):
        self.__name = name
        self.__description = description
        self.__dag = dag
        self.__inputs_schema = inputs_schema
        self.__outputs_schema = outputs_schema
        self.__files_schema = files_schema
        self.__id = None

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @property
    def dag(self):
        return self.__dag

    @property
    def inputs_schema(self):
        return self.__inputs_schema

    @property
    def outputs_schema(self):
        return self.__outputs_schema

    @property
    def files_schema(self):
        return self.__files_schema

    @property
    def id(self):
        return self.__id

    def add_to_account(self, account: Account):

        # check not existing
        if self.__id is not None:
            raise ExistsBackendError('Cannot add workflow definition to account. The '
                                     'workflow definition already exist backend.')

        # make request model
        wf_def_create = WorkflowDefinitionCreate(
            name=self.name,
            description=self.description,
            dag=dict_keys_int_to_str(self.dag.to_dict()),
            inputs_schema=self.inputs_schema,
            outputs_schema=self.outputs_schema,
            files_schema=self.files_schema
        )

        # make rest call
        with RestClient() as client:
            wf_def_model = self._handle_rest_client_call(
                client.new_workflow_definition,
                account.id,
                wf_def_create,
                error_msg='Could not add workflow definition to backend.'
            )

        # update self
        self.__update_from_backend(wf_def_model)

    @classmethod
    def from_project_and_id(cls, project: Project, wf_def_id: str) -> WorkflowDefinition:
        """
        Retrieve a single workflow definition from a project.
        """
        # get workflow definition model
        with RestClient() as client:
            wf_def_model = cls._handle_rest_client_call(
                client.get_workflow_definition_project,
                project.id,
                wf_def_id,
                error_msg='Could not retrieve workflow definition.'
            )
        wf_def = cls.__from_model(wf_def_model)
        return wf_def

    @classmethod
    def list_available_workflow_definitions(cls, project: Project) -> List[dict]:
        """
        Retrieve a list of all available workflow definitions under *project*.
        """
        # get workflow definition models
        with RestClient() as client:
            wf_def_models = cls._handle_rest_client_call(
                client.get_workflow_definition_summaries_project,
                project.id,
                error_msg='Could not retrieve workflow definition summaries.'
            )
        return [wf_def_model.dict() for wf_def_model in wf_def_models]

    @classmethod
    def __from_model(cls, wf_def_model: WorkflowDefinitionModel):
        wf_def = WorkflowDefinition(
            name=wf_def_model.name,
            description=wf_def_model.description,
            dag=dict_keys_int_to_str(DAG.from_dict(wf_def_model.dag)),
            inputs_schema=wf_def_model.inputs_schema,
            outputs_schema=wf_def_model.outputs_schema,
            files_schema=wf_def_model.files_schema
        )
        wf_def.__update_from_backend(wf_def_model)

        return wf_def

    def __update_from_backend(self, wf_def_model: WorkflowDefinitionModel):
        self.__id = wf_def_model.id
