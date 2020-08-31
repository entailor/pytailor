from __future__ import annotations

from enum import Enum
from typing import Optional

from tailor.models import Workflow as WorkflowModel
from tailor.clients import RestClient
from tailor.utils import dict_keys_str_to_int
from .project import Project
from .fileset import FileSet
from .dag import DAG


class WorkflowState(Enum):
    PRE = -3
    ARCHIVED = -2
    FAILED = -1
    STOPPED = 0
    WAITING = 1
    READY = 2
    RESERVED = 3
    RUNNING = 4
    COMPLETED = 5


class Workflow:
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
        self.__state = WorkflowState.PRE
        self.__fileset = fileset or FileSet(self.__project)

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
        return self.__state

    def _update_from_backend(self, wf_model: WorkflowModel):
        # used to set a references to the backend database record for the
        # workflow
        self.__state = WorkflowState[wf_model.state]
        self.__outputs = wf_model.outputs


    @classmethod
    def from_project_and_id(cls, project: Project, wf_id: int) -> Workflow:

        # get workflow model
        with RestClient() as client:
            wf_model = client.get_workflow(project.id, wf_id)

        wf = Workflow(
            project=Project(wf_model.project_id),
            dag=DAG.from_dict(dict_keys_str_to_int(wf_model.dag)),
            name=wf_model.name,
            inputs=wf_model.inputs,
            fileset=wf_model.fileset_id
        )

        wf._update_from_backend(wf_model)

        return wf

    def run(self, mode: str = 'direct', worker_name: Optional[str] = None) -> None:
        """
        Start the workflow.

        """

        if self.state != WorkflowState.PRE:
            pass
            # dont allow run

        if mode == 'direct':
            # starts the DirectRunner
            # blocks until complete
            pass

        elif mode == 'distributed':
            # launches to backend and returns
            pass
