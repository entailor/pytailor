# -*- coding: utf-8 -*-

import importlib
import os
import shutil
import sys
from pathlib import Path

import yaql

from tailor.common.state import State
from tailor.api.dag import TaskType
from tailor.utils import create_rundir, extract_real_filenames, get_logger, list_files
from tailor.utils import format_traceback, get_basenames
from tailor.models import *
from tailor.clients import RestClient, FileClient
from tailor.common.base import APIBase


def _get_expression(arg):
    if isinstance(arg, str) and arg.startswith('<%') and arg.endswith('%>'):
        return arg[2:-2].strip()
    else:
        return False


def _resolve_callable(function_name):
    parts = function_name.split('.')
    func_name = parts[-1]
    module_name = '.'.join(parts[:-1])
    function = getattr(importlib.import_module(module_name), func_name)
    return function


class TaskRunner(APIBase):

    def __init__(self, exec_data: TaskExecutionData, project_id: str):

        self.__set_exec_data(exec_data)
        self.__project_id = project_id

        # get logger
        self.logger = get_logger('JobRunner')

        # create a run directory (here or in self.run?)
        self.run_dir = create_rundir(logger=self.logger)

        self.engine = yaql.factory.YaqlFactory().create()

    def __set_exec_data(self, exec_data: TaskExecutionData):
        self.__context = exec_data.context.dict()
        self.__task = exec_data.task
        self.__fileset_id = exec_data.fileset_id
        self.__run_id = exec_data.run_id

    def run(self):

        self.logger.info(f'Starting task {self.__task.id}')

        # step into run dir
        current_dir = Path.cwd()
        os.chdir(self.run_dir)

        # check in state RUNNING
        task_update = TaskUpdate(
            task_id=self.__task.id,
            state=State.RUNNING.name,
            run_dir=str(self.run_dir)
        )
        with RestClient() as client:
            exec_data = self._handle_rest_client_call(
                client.checkin_task,
                task_update,
                error_msg='Could not check in task.'
            )
        self.__set_exec_data(exec_data)

        # run job in try/except:
        try:
            self.__execute_task()
        except Exception as e:

            state = State.FAILED

            failure_detail = ''.join(format_traceback(e))
            failure_summary = f'Error when executing task {self.__task.id}'
            if hasattr(e, 'message'):
                failure_summary: str = e.message

            # check in state FAILED
            task_update = TaskUpdate(
                run_id=self.__run_id,
                task_id=self.__task.id,
                state=state.name,
                failure_detail=failure_detail,
                failure_summary=failure_summary
            )
            with RestClient() as client:
                exec_data = self._handle_rest_client_call(
                    client.checkin_task,
                    task_update,
                    error_msg='Could not check in task.'
                )
            self.__set_exec_data(exec_data)

            self.logger.error(f'Task {self.__task.id} FAILED', exc_info=True)
        else:
            state = State.COMPLETED

            # check in state COMPLETED
            task_update = TaskUpdate(
                run_id=self.__run_id,
                task_id=self.__task.id,
                state=state.name,
            )
            with RestClient() as client:
                exec_data = self._handle_rest_client_call(
                    client.checkin_task,
                    task_update,
                    error_msg='Could not check in task.'
                )
            self.__set_exec_data(exec_data)

            self.logger.info(f'Task {self.__task.id} COMPLETED successfully')

        # step out of run dir
        os.chdir(current_dir)
        self.__cleanup_after_run(state)
        return True

    def __execute_task(self):
        # call job-type specific code
        task_def = self.__task.definition
        if TaskType(task_def['type']) == TaskType.PYTHON:
            self.__run_python_task(task_def)
        elif TaskType(task_def['type']) == TaskType.BRANCH:
            self.__run_branch_task()

    def __run_python_task(self, task_def):
        parsed_args = self.__determine_args(task_def)
        parsed_kwargs = self.__determine_kwargs(task_def)
        self.__maybe_download_files(task_def)
        function_output = self.__run_function(task_def, parsed_args, parsed_kwargs)
        self.__store_output(task_def, function_output)
        self.__maybe_upload_files(task_def, function_output)

    def __maybe_upload_files(self, task_def, function_output):
        upload = task_def.get('upload')
        # upload must be dict of (tag: val), where val can be:
        #   1:  one or more query expressions(str og list of str) which is applied
        #       to function_output. The query result is searched for file names
        #       pointing to existing files, these files are then uploaded to storage
        #       under the given tag.
        #   2:  one or more glob-style strings (str og list of str) which is applied
        #       in the task working dir. matching files are uploaded under the
        #       given tag.
        if upload:
            files_to_upload = {}
            for tag, v in upload.items():
                if isinstance(v, str):
                    v = [v]
                file_names = []
                for vi in v:
                    if _get_expression(vi):  # alt 1
                        file_names_i = self.__eval_query(_get_expression(vi),
                                                         function_output)
                        file_names_i = extract_real_filenames(file_names_i) or []
                    else:  # alt 2
                        file_names_i = [str(p) for p in list_files(pattern=vi)]
                    file_names.extend(file_names_i)
                # if len(file_names) == 1:
                #     file_names = file_names[0]
                files_to_upload[tag] = file_names

                # DO UPLOAD

                fileset_upload = FileSetUpload(
                    task_id=self.__task.id,
                    tags=get_basenames(files_to_upload)
                )
                # get upload links
                with RestClient() as client:
                    fileset = self._handle_rest_client_call(
                        client.get_upload_urls,
                        self.__project_id,
                        self.__fileset_id,
                        fileset_upload,
                        error_msg='Could not get upload urls.'
                    )
                # do uploads
                with FileClient() as client:
                    client.upload_files(files_to_upload, fileset)

    def __store_output(self, task_def, function_output):
        # TODO: walk function_output and pickle non-JSON objects.
        #       Need a mechanism to persist non-JSON objects on
        #       the storage resource
        outputs = {}
        output_to = task_def.get('output_to')
        if output_to:
            # The entire function_output is put on $.outputs.<output>
            outputs[output_to] = function_output

        output_extraction = task_def.get('output_extraction')
        if output_extraction:
            # For each (tag: query), the query is applied to function_output
            # and the result is put on $.outputs.<tag>
            for k, v in output_extraction.items():
                if _get_expression(v):
                    val = self.__eval_query(_get_expression(v), function_output)
                else:
                    raise ValueError('Bad values for *output_extraction* parameter...')
                outputs[k] = val

        # check in updated outputs
        task_update = TaskUpdate(
            run_id=self.__run_id,
            task_id=self.__task.id,
            outputs=outputs
        )
        with RestClient() as client:
            exec_data = self._handle_rest_client_call(
                client.checkin_task,
                task_update,
                error_msg='Could not check in task.'
            )
        self.__set_exec_data(exec_data)

    def __run_function(self, task_def, args, kwargs):

        # do this so that python modules that have been downloaded are discovered:
        sys.path.append('.')
        # NOTE: this is potentially risky as users can execute arbitrary code by
        #       uploading python modules and calling functions in these modules
        # TODO: use 'sandbox' environment for user provided code?
        #       need to have restrictions on what can run and the python
        #       environment for which functions are executed!
        #       Look into RestrictedPython:
        #       https://github.com/zopefoundation/RestrictedPython

        # run callable
        function_name = task_def['function']
        function = _resolve_callable(function_name)
        self.logger.info(f'Calling: {function_name}')
        function_output = function(*args, **kwargs)
        return function_output

    def __determine_kwargs(self, task_def):
        kwargs = task_def.get('kwargs', {})
        parsed_kwargs = self.__handle_kwargs(kwargs)
        return parsed_kwargs

    def __determine_args(self, task_def):
        args = task_def.get('args', [])
        parsed_args = self.__handle_args(args)
        return parsed_args

    def __maybe_download_files(self, task_def):
        download = task_def.get('download', [])
        download = [download] if isinstance(download, str) else download

        # DO DOWNLOAD
        if download:
            fileset_download = FileSetDownload(
                task_id=self.__task.id,
                tags=download
            )
            # get download links
            with RestClient() as client:
                fileset = self._handle_rest_client_call(
                    client.get_download_urls,
                    self.__project_id,
                    self.__fileset_id,
                    fileset_download,
                    error_msg='Could not get download urls.'
                )
            # do downloads
            with FileClient() as client:
                client.download_files(fileset)

    def __handle_args(self, args):
        if isinstance(args, str) and _get_expression(args):
            parsed_args = self.__eval_query(_get_expression(args), self.__context)
            if not isinstance(parsed_args, list):
                parsed_args = [parsed_args]
            return parsed_args
        elif not isinstance(args, list):
            args = [args]
        parsed_args = []
        for arg in args:
            if _get_expression(arg):
                parsed_arg = self.__eval_query(_get_expression(arg),
                                               self.__context)
                parsed_args.append(parsed_arg)
            else:
                parsed_args.append(arg)
        return parsed_args

    def __handle_kwargs(self, kwargs):
        if isinstance(kwargs, str) and _get_expression(kwargs):
            parsed_kwargs = self.__eval_query(_get_expression(kwargs),
                                              self.__context)

        else:
            parsed_kwargs = {}
            for kw, arg in kwargs.items():
                if _get_expression(arg):
                    parsed_arg = self.__eval_query(_get_expression(arg),
                                                   self.__context)
                    parsed_kwargs[kw] = parsed_arg
                else:
                    parsed_kwargs[kw] = arg
        return parsed_kwargs

    def __run_branch_task(self):

        raise NotImplementedError
        # CHECKIN: tell the backend to perform duplication/branching
        # Backend: self.workflow_service.perform_duplication(self.wf.id, self.task.id)

    def __eval_query(self, expression, data):
        # TODO: use a try/except and give a simpler error than what comes from yaql?
        return self.engine(expression).evaluate(data=data)

    def __cleanup_after_run(self, state):
        # delete run dir
        if state == State.COMPLETED:  # only remove non-empty run dir if COMPLETED
            try:
                shutil.rmtree(self.run_dir, ignore_errors=True)
                self.logger.info('Deleted run dir')
            except:
                self.logger.info('Could not delete run dir', exc_info=1)

            # TODO: trigger additional actions (FUTURE features):
            #   - is this the last job of a COMPLETED workflow:
            #       - if so: cleanup temporary storage, etc.
            #   - is this the last job of a COMPLETED context group:
            #       - if so: do context mapping (update inputs of downstream contexts)

        else:  # always remove empty dirs
            try:
                self.run_dir.rmdir()
                self.logger.info('Deleted empty run dir')
            except:  # non-empty dir, leave as is
                pass


def run_task(checkout: TaskExecutionData, project_id: str):
    runner = TaskRunner(checkout, project_id)
    return runner.run()
