from __future__ import annotations

from typing import Optional
import uuid

from tailor.models import Workflow as WorkflowModel, WorkflowCreate
from tailor.clients import RestClient
from tailor.utils import dict_keys_str_to_int, dict_keys_int_to_str
from tailor.common.state import State
from .base import APIBase
from .project import Project
from .fileset import FileSet
from .dag import DAG


class Workflow(APIBase):
    """
    The Workflow class is used to create new workflows or operate on existing workflows.

    Instantiation patterns:
    - To create a new workflow use the default constructor
    - To retrieve a workflow from the backend use the class methods

    """

    # new workflows are instantiated with __init__
    # existing workflows are instantiated with:
    # - Workflow.from_project_and_id()
    # - Workflow.from_model()

    def __init__(self,
                 project: Project,
                 dag: DAG,
                 name: Optional[str] = None,
                 inputs: Optional[dict] = None,
                 fileset: Optional[FileSet] = None
                 ):
        """
        Create a new workflow.

        Parameters
        ----------
        project : Project
            The project for which to create the workflow.
        dag : DAG
            Provide a dag object for this workflow.
        name : str, optional
            Provide a name for this workflow.
        inputs : dict, optional
            Input data which can be queried from tasks during workflow execution.
            the data must be JSON/BSON serializable.
        fileset : FileSet, optional
            Files to upload is specified in a tag: file(s) dict.
        """

        self.__project = project
        self.__dag = dag
        self.__name = name or 'Unnamed workflow'
        self.__inputs = inputs or {}
        self.__state = State.PRE
        self.__fileset = fileset or FileSet(self.__project)
        self.__outputs = {}

    # use @property to make attributes read-only

    @property
    def project(self):
        return self.__project

    @property
    def dag(self):
        return self.__dag

    @property
    def name(self):
        return self.__name

    @property
    def inputs(self):
        return self.__inputs

    @property
    def state(self):
        return self.__state.name

    @property
    def outputs(self):
        return self.__outputs

    def _update_from_backend(self, wf_model: WorkflowModel):
        # used to set a references to the backend database record for the
        # workflow
        self.__state = State[wf_model.state]
        self.__outputs = wf_model.outputs

    @classmethod
    def from_project_and_id(cls, project: Project, wf_id: int) -> Workflow:

        # get workflow model
        with RestClient() as client:
            wf_model = cls._handle_rest_client_call(
                client.get_workflow,
                project.id,
                wf_id,
                error_msg='Could not retrieve workflow.'
            )

        wf = Workflow(
            project=Project(wf_model.project_id),
            dag=DAG.from_dict(dict_keys_str_to_int(wf_model.dag)),
            name=wf_model.name,
            inputs=wf_model.inputs,
            fileset=wf_model.fileset_id
        )

        wf._update_from_backend(wf_model)

        return wf

    def run(self, mode: str = 'here_and_now', worker_name: Optional[str] = None) -> None:
        """
        Start the workflow.

        **Parameters**

        - **mode** (str, Optional)
            If 'here_and_now' (default) the workflow is executed immediately in the
            current python process. Useful for development and debugging.
            If 'distributed' the workflow will be launched to the database, and tasks
            will be executed in parallel on one or more workers.
        - **worker_name** (str, Optional)
            A worker name can be provided to control which worker(s) will execute the
            workflow's tasks. This parameter is ignored for *mode='here_and_now'*

        """

        if self.__state != State.PRE:
            # don't allow run, warn or raise
            return

        if mode == 'here_and_now':
            worker_name = uuid.uuid4()

        # create data model
        create_data = WorkflowCreate(
            dag=dict_keys_int_to_str(self.dag.to_dict()),
            name=self.name,
            inputs=self.inputs,
            fileset_id=self.__fileset.id,
            worker_name=worker_name
        )

        # add workflow to backend
        with RestClient() as client:
            wf_model = self._handle_rest_client_call(
                client.create_workflow,
                self.__project.id,
                create_data,
                error_msg='Could not create workflow.'
            )
            self._update_from_backend(wf_model)

        if mode == 'here_and_now':
            # starts the DirectRunner
            # blocks until complete
            pass

        elif mode == 'distributed':
            # launches to backend and returns
            pass
