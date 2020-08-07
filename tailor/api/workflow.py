# -*- coding: utf-8 -*-
from typing import Optional

from . import Project
from . import TaskDefinition
# from .workflow_run import WorkflowRun
from tailor.utils import get_logger


class Workflow:
    """
    A Workflow represents a workflow during its specification phase.

    Parameters
    ----------
    project : Project
        The project for which to create the workflow.
    task_def : TaskDefinition, optional
        A task definition.
    name : str, optional
        Provide a name for this workflow.
    inputs : dict, optional
        Input data which can be queried from tasks during workflow execution.
        the data must be JSON/BSON serializable.
    files : dict, optional
        Files to upload is specified in a tag: file(s) dict.
    worker : str, optional
        Provide a worker name for the to run the workflow.
    mode : str, optional
        "serial" or "parallel".

    """

    def __init__(self, project: Project, task_def: Optional[TaskDefinition] = None,
                 name: Optional[str] = None, inputs: dict = None, files: dict = None,
                 worker: Optional[str] = None, mode: str = None):
        self.project = project
        self.task_def = task_def
        self.name = name
        self.inputs = inputs
        self.files = files
        self.worker = worker
        self.mode = mode or 'serial'

    def __assert_can_run(self):
        """Make sure that all data required to run are defined and correct."""
        # TODO: implement this method
        pass

    # def run(self) -> WorkflowRun:
    #     """
    #     Start running this workflow.
    #
    #     Returns
    #     -------
    #     WorkflowRun
    #         A Workflow run object representing the executed workflow.
    #
    #     """
    #     logger = get_logger('Workflow')
    #     storage_key = self.__storage_service.new_storage_key()
    #     if self.files is not None:
    #         for tag, fname in self.files.items():
    #             self.__storage_service.upload(storage_key, fname, tag=tag)
    #
    #     if self.mode == 'serial':
    #         if self.worker is not None:
    #             logger.warn(f'Specifying a worker (worker="{self.worker}") has no '
    #                         'effect when mode="serial"')
    #         return self.__run_serial(storage_key)
    #     elif self.mode == 'parallel':
    #         return self.__launch(storage_key)
    #     else:
    #         raise ValueError('mode must be "serial" or "parallel"')
    #
    # def __run_serial(self, storage_key) -> WorkflowRun:
    #     self.__assert_can_run()
    #     from tailor.internal.execution import SerialRunner
    #
    #     runner = SerialRunner(self.__project)
    #     wf_id = runner.run_workflow(self.task_def,
    #                                 self.name,
    #                                 self.inputs,
    #                                 storage_key)
    #     return WorkflowRun(self.__project, wf_id)
    #
    # def __launch(self, storage_key) -> WorkflowRun:
    #     self.__assert_can_run()
    #
    #     from tailor import Configuration
    #     authorizations = Configuration.Instance().authorizations
    #
    #     wf_model = self.__workflow_service.create(self.task_def,
    #                                               self.__project,
    #                                               authorizations.user,
    #                                               self.name,
    #                                               self.inputs,
    #                                               storage_key,
    #                                               self.worker)
    #     return WorkflowRun(self.__project, wf_model.id)
