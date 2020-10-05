import asyncio
import concurrent.futures
import logging
from typing import Optional
import httpx

from pytailor import Project, WorkflowDefinition
import importlib
import uuid
import os

from pytailor.config import LOGGING_FORMAT
from pytailor.execution.taskrunner import run_task
from pytailor.models import TaskCheckout, TaskExecutionData
from pytailor.utils import get_logger
from pytailor.clients import AsyncRestClient
from pytailor.exceptions import BackendResponseError


async def do_checkout(checkout_query: TaskCheckout) -> Optional[TaskExecutionData]:
    async with AsyncRestClient() as client:
        try:
            exec_data = await client.checkout_task(checkout_query)
        except httpx.HTTPError as exc:
            raise BackendResponseError(
                f"Error while checking out task. The response " f"was: {str(exc)}."
            )
    return exec_data


async def async_run_task(pool, task_execution_data: TaskExecutionData):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(pool, run_task, task_execution_data)
    return result


# job run-manager
async def run_manager(checkout_query: TaskCheckout, n_cores, sleep):

    # set up logging
    core_report_format = LOGGING_FORMAT + f" (%(n)s/{n_cores} cores in use)"
    formatter = logging.Formatter(core_report_format)
    logger = get_logger("Worker", formatter=formatter)
    n_running = 0
    extra = {"n": n_running}
    logger = logging.LoggerAdapter(logger, extra)

    # helper to handle finished asyncio_tasks
    def handle_finished(aio_tasks):
        for aio_task in list(aio_tasks):
            if aio_task.done():
                aio_tasks.remove(aio_task)
                print("Task finished", aio_task.result())

    # go into loop with process pool
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_cores) as pool:
        try:

            asyncio_tasks = set()

            while True:

                n_running = len(asyncio_tasks)
                extra["n"] = n_running  # update running for logging

                if n_running < n_cores:
                    # worker can checkout task
                    task_exec_data = await do_checkout(checkout_query)

                    if task_exec_data:
                        logger.info(
                            f"Task available, starting run for task"
                            f"{task_exec_data.task.id}"
                        )
                        asyncio_task = asyncio.create_task(
                            async_run_task(pool, task_exec_data)
                        )
                        asyncio_tasks.add(asyncio_task)
                        await asyncio.sleep(0.3)  # needed?
                        handle_finished(asyncio_tasks)

                    else:
                        logger.info(f"No jobs available, waiting {sleep} seconds")
                        await asyncio.sleep(sleep)
                        handle_finished(asyncio_tasks)

                else:
                    logger.info(f"All cores in use, waiting {sleep} seconds")
                    await asyncio.sleep(sleep)
                    handle_finished(asyncio_tasks)

        except asyncio.CancelledError:
            pass  # TODO recover or die?
            # print('\excepted CanceledError\n')

        # TODO: do graceful handling of non-finished tasks on worker errors, e.g:
        #       - try to checkin FAILED with a meaningful error message,
        #       - or try to reset tasks for re-execution elsewhere


def run_worker(sleep, n_cores, worker_name, project_ids):
    checkout_query = TaskCheckout(
        worker_capabilities=["python"],
        worker_name=worker_name,
        projects=project_ids or None,
    )

    try:
        asyncio.run(run_manager(checkout_query, int(n_cores), int(sleep)))
    except KeyboardInterrupt:
        print("CTRL-C pressed, exiting...")


def test_worker(project_name):

    def get_all_tasks(dag_dict, all_tasks):
        if isinstance(dag_dict, dict):
            all_tasks.append(dag_dict)
        if dag_dict.get("tasks"):
            for task in dag_dict["tasks"]:
                get_all_tasks(task, all_tasks)
        if dag_dict.get("task"):
            if dag_dict["task"].get("tasks"):
                for task in dag_dict["task"]["tasks"]:
                    get_all_tasks(task, all_tasks)
            else:
                get_all_tasks(dag_dict["task"], all_tasks)
        return all_tasks

    def test_all_function_imports_in_project(project):
        wf_dfs_info = []
        test_report = []
        tsts_ok = True
        for wf_def_info in project.list_available_workflow_definitions():
            test_report_string = "testing workflow definition: " + wf_def_info["name"]
            test_report.extend('### ' + test_report_string + "\n")
            wf_def = WorkflowDefinition.from_project_and_id(project, wf_def_info["id"])
            wf_df_ok, report_string = test_import_functions_in_tasks(get_all_tasks(wf_def.dag.to_dict(), [])[1:])
            wf_def_info["test_ok"] = wf_df_ok
            wf_def_info.pop("description")
            wf_dfs_info.append(wf_def_info)
            test_report.extend(report_string)
            if not wf_df_ok:
                tsts_ok = False

        return tsts_ok, wf_dfs_info, ''.join(test_report)

    def test_import_functions_in_tasks(tasks_list):
        test_ok = True
        report_string = []
        for task in tasks_list:
            print_string = "testing task: " + task["name"]
            report_string.append(print_string + "\n\n")
            if task.get("function"):
                print_string = "trying to import function: " + task["function"]
                report_string.append(print_string + "\n\n")
                import_string = task["function"].rsplit(".", 1)
                try:
                    importlib.import_module(import_string[0], import_string[1])
                    print_string = "import ok"
                    report_string.append(print_string + "\n")
                except ModuleNotFoundError as error:
                    print(print_string + "\n")
                    print_string = error.__str__()
                    report_string.append(print_string + "\n")
                    test_ok = False
                    print(print_string)
            else:
                print_string = "task has no function"
                report_string.append(print_string + "\n")

        return test_ok, report_string

    # TODO: When project_id_filter is implemented, loop over all projects:
    #  for prj_id = project_id_filter: prj = Project.from_id(prj_id)
    prj = Project.from_name(project_name)
    tests_ok, wf_defs_info, main_report_string = test_all_function_imports_in_project(prj)
    if not tests_ok:
        test_report_filename = f"test_report_{uuid.uuid1()}.MD"
        with open(test_report_filename, "w") as f:
            f.write(main_report_string)
        print("Tests failed. See full report here:", os.path.abspath(test_report_filename))
    else:
        print("Tests ran OK")
    return wf_defs_info
