from __future__ import annotations

import uuid
from collections import defaultdict
from typing import Optional

from pytailor.clients import RestClient
from pytailor.common.base import APIBase
from pytailor.exceptions import BackendResourceError
from pytailor.execution import SerialRunner
from pytailor.models import Workflow as WorkflowModel, WorkflowCreate, TaskState, \
    TaskOperation, TaskOperationType
from pytailor.utils import dict_keys_str_to_int, dict_keys_int_to_str

from .dag import DAG
from .fileset import FileSet
from .project import Project


class Workflow(APIBase):
    """
    The Workflow class is used to create new workflows or operate on existing workflows.

    **Instantiation patterns:**
    - To create a new workflow from a DAG use the default constructor
    - To create a new workflow from a workflow definition use
    *Workflow.from_definition_id()*
    - To retrieve a workflow from the backend use *Workflow.from_project_and_id()*

    """

    # new workflows are instantiated with __init__
    # existing workflows are instantiated with:
    # - Workflow.from_project_and_id()

    def __init__(
        self,
        project: Project,
        dag: DAG,
        name: Optional[str] = None,
        inputs: Optional[dict] = None,
        fileset: Optional[FileSet] = None,
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
        self.__name = name or "Unnamed workflow"
        self.__inputs = inputs or {}
        self.__state = None
        self.__fileset = fileset or FileSet(self.__project)
        self.__outputs = {}
        self.__id = None
        self.__model = None
        self.__wf_def_id = None

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

    @property
    def fileset(self):
        return self.__fileset

    @property
    def outputs(self):
        return self.__outputs

    @property
    def id(self):
        return self.__id

    @property
    def wf_def_id(self):
        return self.__wf_def_id

    @wf_def_id.setter
    def wf_def_id(self, wf_def_id: str):
        if not self.__wf_def_id:
            self.__wf_def_id = wf_def_id
        else:
            raise AttributeError("wf_def_id already set")

    def __str__(self):
        return self.__pretty_printed()

    def __update_from_backend(self, wf_model: WorkflowModel):
        # used to set a references to the backend database record for the
        # workflow
        self.__state = wf_model.state
        self.__outputs = wf_model.outputs
        self.__id = wf_model.id
        self.__wf_def_id = wf_model.from_definition_id
        self.__model = wf_model

    def reset_task(self, task_id: str):
        """Reset task."""
        self.__assert_has_state()
        task_operation = TaskOperation(
            type=TaskOperationType.RESET,
        )
        with RestClient() as client:
            self._handle_request(
                client.perform_task_operation,
                self.id,
                self.project.id,
                task_id,
                task_operation,
                error_msg=f"Could not reset task {task_id}"
            )

    def refresh(self) -> None:
        """Update with latest data from backend."""
        self.__assert_has_state()
        wf_model = self.__fetch_model(self.project.id, self.id)
        self.__update_from_backend(wf_model)

    @classmethod
    def __fetch_model(cls, project_id: str, wf_id: str) -> WorkflowModel:
        with RestClient() as client:
            return cls._handle_request(
                client.get_workflow,
                project_id,
                wf_id,
                error_msg="Could not retrieve workflow.",
            )

    @classmethod
    def from_project_and_id(cls, project: Project, wf_id: int) -> Workflow:
        """
        Retrieve a workflow from the backend.
        """
        wf_model = cls.__fetch_model(project.id, str(wf_id))
        wf = Workflow(
            project=Project(wf_model.project_id),
            dag=DAG.from_dict(dict_keys_str_to_int(wf_model.dag)),
            name=wf_model.name,
            inputs=wf_model.inputs,
            fileset=FileSet(Project(wf_model.project_id), wf_model.fileset_id)
        )
        wf.__update_from_backend(wf_model)
        return wf

    @classmethod
    def from_definition_id(cls, project: Project,
                           wf_def_id: str,
                           name: Optional[str] = None,
                           inputs: Optional[dict] = None,
                           fileset: Optional[FileSet] = None
                           ) -> Workflow:
        """
        Create a new workflow from an existing workflow definition.
        """
        with RestClient() as client:
            wf_def_model = cls._handle_request(
                client.get_workflow_definition_project,
                project.id,
                wf_def_id,
                error_msg="Error while fetching workflow definition.",
            )
        wf = Workflow(
            project=project,
            dag=DAG.from_dict(dict_keys_str_to_int(wf_def_model.dag)),
            name=name,
            inputs=inputs,
            fileset=fileset
        )
        wf.wf_def_id = wf_def_id
        return wf

    def run(self, distributed: bool = False, worker_name: Optional[str] = None) -> None:
        """
        Start the workflow.

        **Parameters**

        - **distributed** (bool, Optional) If False (default) the workflow is executed
        immediately in the current python process one task at a time. Useful for
        development and debugging. If True the workflow will be launched to
        the database, and tasks will be executed in parallel on one or more workers.
        - **worker_name** (str, Optional) A worker name can be provided to control which
        worker(s) will execute the workflow's tasks. This parameter is ignored for
        *distributed=False*
        """

        if self.__state:
            raise BackendResourceError("Cannot run an existing workflow.")

        if not distributed:
            worker_name = str(uuid.uuid4())

        # create data model
        create_data = WorkflowCreate(
            name=self.name,
            inputs=self.inputs,
            fileset_id=self.__fileset.id,
            worker_name_restriction=worker_name,
        )

        if self.__wf_def_id:
            create_data.from_definition_id = self.__wf_def_id
        else:
            create_data.dag = dict_keys_int_to_str(self.dag.to_dict())

        # add workflow to backend
        with RestClient() as client:
            wf_model = self._handle_request(
                client.new_workflow,
                self.__project.id,
                create_data,
                error_msg="Could not create workflow.",
            )
            self.__update_from_backend(wf_model)

        if not distributed:
            # starts the SerialRunner
            # blocks until complete
            requirements = self.dag.get_all_requirements()
            runner = SerialRunner(self.project.id, worker_name, wf_model.id,
                                  capabilities=requirements)
            runner.run()

            # get the updated workflow and update self
            self.refresh()

        # else:
        #     # launches to backend and returns
        #     # no actions needed here
        #     raise NotImplementedError

    def __assert_has_state(self):
        if not self.__state:
            raise BackendResourceError(
                "This workflow has not been run yet."
            )

    def __pretty_printed(self):
        lines = []
        # columns
        tf = "{:^6.6}"  # task id
        n1 = "{:<21.20}"  # name
        p1 = "{:^22.21}"  # parents
        n2 = "{:<19.19}.."  # name
        p2 = "{:^20.20}.."  # parents
        typ = "{:^12.12}"  # type
        s = "{:^12.12}"  # state

        row = "|" + tf + "|" + n1 + "|" + p1 + "|" + typ + "|" + s + "|\n"
        top = "+" + "-" * 77 + "+" + "\n"
        vsep = (
                "+"
                + "-" * 6
                + "+"
                + "-" * 21
                + "+"
                + "-" * 22
                + "+"
                + "-" * 12
                + "+"
                + "-" * 12
                + "+\n"
        )
        header = f"| Workflow {self.id}: {self.name}"
        header = header + " " * (78 - len(header)) + "|\n"
        colheader = row.format("id", " Task name", "Parents", "Type", "State")
        lines.append(top)
        lines.append(header)
        lines.append(vsep)
        lines.append(colheader)
        lines.append(vsep)

        added_tasks = set()
        rows_dict = {}
        id_task_mapping = {t.id: t for t in self.__model.tasks}
        parent_links = defaultdict(list)
        for p, c in self.__model.task_links.items():
            for ci in c:
                parent_links[str(ci)].append(int(p))

        def add_row(tid):
            if not tid in added_tasks:
                added_tasks.add(tid)
                t = id_task_mapping[tid]
                task_name = " " + t.name
                n = n1 if len(task_name) < 21 else n2
                parents = str(parent_links[tid])[1:-1] if tid in parent_links else "-"
                p = p1 if len(parents) < 22 else p2
                row = "|" + tf + "|" + n + "|" + p + "|" + typ + "|" + s + "|\n"
                rows_dict[tid] = row.format(
                    str(tid),
                    task_name,
                    parents,
                    t.type.upper(),
                    self.__model.task_states[tid],
                )

                for cid in self.__model.task_links[tid]:
                    add_row(str(cid))

        for rt_id in self.__model.root_tasks:
            add_row(rt_id)

        lines.extend([v for k, v in sorted(rows_dict.items())])
        lines.append(vsep)

        return "".join(lines)
