import importlib
import os
import random
import shutil
import time
from pathlib import Path

from jsonpath_ng import parse

from pytailor.api.dag import TaskType
from pytailor.utils import (
    create_rundir,
    extract_real_filenames,
    get_logger,
    list_files,
    as_query,
    format_traceback,
    get_basenames,
    walk_and_apply
)
from pytailor.models import *
from pytailor.clients import RestClient, FileClient
from pytailor.common.base import APIBase
from pytailor.exceptions import BackendResponseError, QueryError
from pytailor.config import WAIT_RETRY_COUNT, WAIT_SLEEP_TIME


def _resolve_callable(function_name):
    parts = function_name.split(".")
    func_name = parts[-1]
    module_name = ".".join(parts[:-1])
    function = getattr(importlib.import_module(module_name), func_name)
    return function


MAX_SLEEP_TIME = 60


def _get_sleep_time_seconds(n):
    exp_backoff = 2 ** n
    jitter = random.random()
    return min(exp_backoff + jitter, MAX_SLEEP_TIME)


class TaskRunner(APIBase):
    def __init__(self, exec_data: TaskExecutionData):

        self.__set_exec_data(exec_data)

        # get logger
        self.logger = get_logger("TaskRunner")

        # create a run directory (here or in self.run?)
        self.run_dir = create_rundir(logger=self.logger)

        self.state = TaskState.RESERVED

    def __set_exec_data(self, exec_data: TaskExecutionData):
        self.__context = exec_data.context.dict() if exec_data.context else None
        self.__task_id = exec_data.task_id
        self.__definition = exec_data.definition
        self.__name = self.__definition["name"] if self.__definition else None
        self.__fileset_id = exec_data.fileset_id
        self.__run_id = exec_data.run_id
        self.__project_id = exec_data.project_id

    def __update_exec_data(self, exec_data: TaskExecutionData):
        self.__context = exec_data.context.dict() if exec_data.context \
            else self.__context
        self.__task_id = exec_data.task_id or self.__task_id
        self.__definition = exec_data.definition or self.__definition
        self.__name = self.__definition["name"] if self.__definition else self.__name
        self.__fileset_id = exec_data.fileset_id or self.__fileset_id
        self.__run_id = exec_data.run_id or self.__run_id
        self.__project_id = exec_data.project_id or self.__project_id

    def run(self):

        self.state = TaskState.RUNNING
        self.logger.info(f"Starting task {self.__task_id}: {self.__name}")

        # step into run dir
        current_dir = Path.cwd()
        os.chdir(self.run_dir)

        # run job in try/except:
        try:
            self.__execute_task()
        except Exception as e:
            self.__checkin_failed(e)

        # step out of run dir
        os.chdir(current_dir)
        self.__cleanup_after_run()
        return True

    def __execute_task(self):
        # call job-type specific code
        task_def = self.__definition
        if TaskType(task_def["type"]) == TaskType.PYTHON:
            self.__run_python_task(task_def)
        elif TaskType(task_def["type"]) == TaskType.BRANCH:
            self.__run_branch_task()

    def __run_python_task(self, task_def):
        # check in state RUNNING, and get exec data
        task_update = TaskUpdate(
            task_id=self.__task_id, state=self.state, run_dir=str(self.run_dir)
        )
        with RestClient() as client:
            exec_data = self._handle_request(
                client.checkin_task, task_update, error_msg="Could not check in task."
            )
            self.__update_exec_data(exec_data)
            exec_data = self.__wait_for_task_result(
                client.get_task_result,
                exec_data.processing_id,
                error_msg="Could not perform branching.",
            )
        self.__update_exec_data(exec_data)

        parsed_args = self.__determine_args(task_def)
        parsed_kwargs = self.__determine_kwargs(task_def)
        self.__maybe_download_files(task_def)
        function_output = self.__run_function(task_def, parsed_args, parsed_kwargs)
        self.__store_output(task_def, function_output)
        self.__maybe_upload_files(task_def, function_output)
        self.__checkin_completed()

    def __maybe_upload_files(self, task_def, function_output):
        upload = task_def.get("upload")
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
                    if as_query(vi):  # alt 1
                        file_names_i = self.__eval_query(as_query(vi), function_output)
                        file_names_i = extract_real_filenames(file_names_i) or []
                    else:  # alt 2
                        file_names_i = [str(p) for p in list_files(pattern=vi)]
                    file_names.extend(file_names_i)
                # if len(file_names) == 1:
                #     file_names = file_names[0]
                files_to_upload[tag] = file_names

                # DO UPLOAD

                fileset_upload = FileSetUpload(
                    task_id=self.__task_id, tags=get_basenames(files_to_upload)
                )
                # get upload links
                with RestClient() as client:
                    fileset = self._handle_request(
                        client.get_upload_urls,
                        self.__project_id,
                        self.__fileset_id,
                        fileset_upload,
                        error_msg="Could not get upload urls.",
                    )
                # do uploads
                with FileClient() as client:
                    self._handle_request(
                        client.upload_files,
                        files_to_upload,
                        fileset
                    )

    def __store_output(self, task_def, function_output):
        outputs = {}
        output_to = task_def.get("output_to")
        if output_to:
            # The entire function_output is put on $.outputs.<output>
            outputs[output_to] = function_output

        output_extraction = task_def.get("output_extraction")
        if output_extraction:
            # For each (tag: query), the query is applied to function_output
            # and the result is put on $.outputs.<tag>
            for k, v in output_extraction.items():
                q = as_query(v)
                if q or q == "":
                    val = self.__eval_query(q, function_output)
                else:
                    raise ValueError("Bad values for *output_extraction* parameter...")
                outputs[k] = val

        # check in updated outputs
        task_update = TaskUpdate(
            run_id=self.__run_id, task_id=self.__task_id, outputs=outputs
        )
        with RestClient() as client:
            exec_data = self._handle_request(
                client.checkin_task, task_update, error_msg="Could not check in task."
            )
        self.__update_exec_data(exec_data)

    def __run_function(self, task_def, args, kwargs):

        # DONT do this:
        # sys.path.append('.')
        # this has the effect that python modules that have been downloaded are
        # discovered this is potentially risky as users can execute arbitrary code by
        # uploading python modules and calling functions in these modules

        # TODO: use 'sandbox' environment?
        #       need to have restrictions on what can run and the python
        #       environment for which functions are executed!
        #       Look into RestrictedPython:
        #       https://github.com/zopefoundation/RestrictedPython

        # run callable
        function_name = task_def["function"]
        function = _resolve_callable(function_name)
        self.logger.info(f"Calling: {function_name}")
        function_output = function(*args, **kwargs)
        return function_output

    def __determine_kwargs(self, task_def):
        kwargs = task_def.get("kwargs", {})
        parsed_kwargs = self.__handle_kwargs(kwargs)
        return parsed_kwargs

    def __determine_args(self, task_def):
        args = task_def.get("args", [])
        parsed_args = self.__handle_args(args)
        return parsed_args

    def __maybe_download_files(self, task_def):
        download = task_def.get("download", [])
        download = [download] if isinstance(download, str) else download

        # DO DOWNLOAD
        if download:
            use_storage_dirs = task_def.get("use_storage_dirs", True)
            fileset_download = FileSetDownload(task_id=self.__task_id, tags=download)
            # get download links
            with RestClient() as client:
                fileset = self._handle_request(
                    client.get_download_urls,
                    self.__project_id,
                    self.__fileset_id,
                    fileset_download,
                    error_msg="Could not get download urls.",
                )
            # do downloads
            with FileClient() as client:
                self._handle_request(
                    client.download_files,
                    fileset,
                    use_storage_dirs
                )

    def __handle_args(self, args):
        q = as_query(args)
        if q:
            parsed_args = self.__eval_query(q, self.__context)
            if not isinstance(parsed_args, list):
                raise TypeError(
                    f"Query expression must evaluate to list. Got "
                    f"{type(parsed_args)}"
                )
        elif not isinstance(args, list):
            raise TypeError(
                f"*args* must be list or query-expression. Got {type(args)}"
            )
        else:
            parsed_args = self.__eval_nested(args)
        return parsed_args

    def __handle_kwargs(self, kwargs):
        q = as_query(kwargs)
        if q:
            parsed_kwargs = self.__eval_query(q, self.__context)
            if not isinstance(parsed_kwargs, dict):
                raise TypeError(
                    f"Query expression must evaluate to dict. Got "
                    f"{type(parsed_kwargs)}"
                )
        elif not isinstance(kwargs, dict):
            raise TypeError(
                f"*kwargs* must be dict or query-expression. Got " f"{type(kwargs)}"
            )
        else:
            parsed_kwargs = self.__eval_nested(kwargs)
        return parsed_kwargs

    def __run_branch_task(self):

        task_update = TaskUpdate(
            task_id=self.__task_id, perform_branching=True, state=self.state,
            run_dir=str(self.run_dir)
        )
        with RestClient() as client:
            exec_data = self._handle_request(
                client.checkin_task,
                task_update,
                error_msg="Could not perform branching.",
            )
            self.__update_exec_data(exec_data)
            exec_data = self.__wait_for_task_result(
                client.get_task_result,
                exec_data.processing_id,
                error_msg="Could not perform branching.",
            )
        self.__update_exec_data(exec_data)
        # dont need to check in completed which is already done backend
        # just update state locally
        self.state = TaskState.COMPLETED

    def __eval_query(self, expression, data):
        vals = [match.value for match in parse(expression).find(data)]
        if not vals:
            raise QueryError(f"Query expression {expression} did not return any data.")
        if len(vals) == 1:
            return vals[0]
        else:
            return vals

    def __eval_nested(self, data):
        val_apply = lambda v: self.__eval_query(as_query(v), self.__context)
        return walk_and_apply(data, val_cond=as_query, val_apply=val_apply)

    def __cleanup_after_run(self):
        # delete run dir
        if self.state is TaskState.COMPLETED:  # only remove non-empty run dir if COMPLETED
            try:
                shutil.rmtree(self.run_dir, ignore_errors=True)
                self.logger.info("Deleted run dir")
            except:
                self.logger.info("Could not delete run dir", exc_info=1)
        else:  # always remove empty dirs
            try:
                self.run_dir.rmdir()
                self.logger.info("Deleted empty run dir")
            except:  # non-empty dir, leave as is
                pass

    def __checkin_failed(self, e: Exception):
        self.state = TaskState.FAILED

        failure_detail = "".join(format_traceback(e))
        failure_summary = f"Error when executing task {self.__task_id}"
        if hasattr(e, "message"):
            failure_summary: str = e.message

        # check in state FAILED
        task_update = TaskUpdate(
            run_id=self.__run_id,
            task_id=self.__task_id,
            state=self.state,
            failure_detail=failure_detail,
            failure_summary=failure_summary,
        )
        with RestClient() as client:
            exec_data = self._handle_request(
                client.checkin_task,
                task_update,
                error_msg="Could not check in task.",
            )
        self.__update_exec_data(exec_data)

        self.logger.error(f"Task {self.__task_id} FAILED", exc_info=True)

    def __checkin_completed(self):
        self.state = TaskState.COMPLETED

        # check in state COMPLETED
        task_update = TaskUpdate(
            run_id=self.__run_id,
            task_id=self.__task_id,
            state=self.state,
        )
        with RestClient() as client:
            exec_data = self._handle_request(
                client.checkin_task,
                task_update,
                error_msg="Could not check in task.",
            )
        self.__update_exec_data(exec_data)

        self.logger.info(f"Task {self.__task_id} COMPLETED successfully")

    def __wait_for_task_result(self, *args, **kwargs) -> Any:
        retries = 0
        time.sleep(_get_sleep_time_seconds(retries))
        response = self._handle_request(*args, **kwargs)
        if response.processing_status is ProcessingStatus.PENDING:
            while response.processing_status is ProcessingStatus.PENDING:
                retries += 1
                self.logger.info("Waiting for result from backend")
                time.sleep(_get_sleep_time_seconds(retries))
                response = self._handle_request(*args, **kwargs)
                if retries > WAIT_RETRY_COUNT:
                    raise BackendResponseError("Failed to retrieve result from "
                                               "backend")
        return response


def run_task(checkout: TaskExecutionData):
    runner = TaskRunner(checkout)
    return runner.run()
