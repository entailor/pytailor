import datetime
import importlib
import os
import uuid
from typing import Optional, List, TextIO

from pytailor.clients import RestClient
from pytailor.common.request_handler import handle_request


def _get_all_tasks(dag_dict, all_tasks):
    if isinstance(dag_dict, dict):
        all_tasks.append(dag_dict)
    if dag_dict.get("tasks"):
        for task in dag_dict["tasks"]:
            _get_all_tasks(task, all_tasks)
    if dag_dict.get("task"):
        if dag_dict["task"].get("tasks"):
            for task in dag_dict["task"]["tasks"]:
                _get_all_tasks(task, all_tasks)
        else:
            _get_all_tasks(dag_dict["task"], all_tasks)
    return all_tasks


def _check_all_function_imports_in_project(project_id: str, log_file: TextIO):
    wf_defs_info = []
    tests_ok = True
    with RestClient() as client:
        wf_def_summaries = handle_request(
            client.get_workflow_definition_summaries_project, project_id
        )
    if not wf_def_summaries:
        log_file.write("No workflow definitions for project\n")
    for wf_def_info in wf_def_summaries:
        log_file.write(f"Checking workflow definition: "
                       f"{wf_def_info.name} ({wf_def_info.id})\n")
        wf_def_check_summary = {"id": wf_def_info.id, "name": wf_def_info.name}
        with RestClient() as client:
            wf_def = handle_request(
                client.get_workflow_definition_project, project_id, wf_def_info.id
            )
        wf_df_ok = _check_import_functions_in_tasks(
            _get_all_tasks(wf_def.dag, [])[1:], log_file
        )
        wf_def_check_summary["test_ok"] = wf_df_ok
        wf_defs_info.append(wf_def_check_summary)
        if not wf_df_ok:
            tests_ok = False
        log_file.write("\n")
    return tests_ok, wf_defs_info


def _check_import_functions_in_tasks(tasks_list, log_file):
    test_ok = True
    for task in tasks_list:
        log_file.write(f"Testing task: {task['name']}\n")
        if task.get("function"):
            log_file.write(f"Trying to import function: {task['function']}\n")
            import_string = task["function"].rsplit(".", 1)
            try:
                importlib.import_module(import_string[0], import_string[1])
                log_file.write("Import OK\n")
            except ModuleNotFoundError as error:
                log_file.write(f"Import NOT OK: {str(error)}\n")
                test_ok = False
        else:
            log_file.write("Task has no function\n")

    return test_ok


def workflow_definition_compliance_test(project_ids: Optional[List[str]]):
    """
    Check that python functions referenced in workflow definitions are importable.
    """
    wf_defs_info = []

    with RestClient() as client:
        projects = handle_request(client.get_projects)
    if project_ids:
        projects = [project for project in projects if project.id in project_ids]

    now_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    log_file_name = f"worker_check_{now_str}.log"
    compliance = True
    with open(log_file_name, "w") as log_file:
        for project in projects:
            log_file.write(f"Checking project: {project.name} ({project.id})\n\n")
            (
                tests_ok,
                wf_defs_info_prj,
            ) = _check_all_function_imports_in_project(project.id, log_file)
            if not tests_ok:
                print(
                    f"Tests failed for workflow definitions in project {project.name}. "
                    f"See log file for details."
                )
                compliance = False
            wf_defs_info.extend(wf_defs_info_prj)
            log_file.write("\n")

    if compliance:
        os.remove(log_file_name)

    return wf_defs_info
