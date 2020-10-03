import importlib
import os
import uuid
from typing import Optional, List

from pytailor.clients import RestClient
from pytailor.common.rest_call_handler import handle_rest_client_call


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


def _check_all_function_imports_in_project(project_id):
    wf_defs_info = []
    test_report = []
    tests_ok = True
    with RestClient() as client:
        wf_def_summaries = handle_rest_client_call(
            client.get_workflow_definition_summaries_project, project_id
        )
    for wf_def_info in wf_def_summaries:
        test_report_string = "testing workflow definition: " + wf_def_info.name
        test_report.extend("### " + test_report_string + "\n")
        wf_def_check_summary = {"id": wf_def_info.id}
        with RestClient() as client:
            wf_def = handle_rest_client_call(
                client.get_workflow_definition_project, project_id, wf_def_info.id
            )
        wf_df_ok, report_string = _check_import_functions_in_tasks(
            _get_all_tasks(wf_def.dag, [])[1:]
        )
        wf_def_check_summary["test_ok"] = wf_df_ok
        wf_defs_info.append(wf_def_check_summary)
        test_report.extend(report_string)
        if not wf_df_ok:
            tests_ok = False
    return tests_ok, wf_defs_info, "".join(test_report)


def _check_import_functions_in_tasks(tasks_list):
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


def workflow_definition_compliance_test(project_ids: Optional[List[str]]):
    """"""
    wf_defs_info = []
    if not project_ids:
        with RestClient() as client:
            projects = handle_rest_client_call(client.get_projects)

    for project in projects:
        (
            tests_ok,
            wf_defs_info,
            main_report_string,
        ) = _check_all_function_imports_in_project(project.id)
        if not tests_ok:
            test_report_filename = f"test_report_{uuid.uuid1()}.MD"
            with open(test_report_filename, "w") as f:
                f.write(main_report_string)
            print(
                "Tests failed. See full report here:",
                os.path.abspath(test_report_filename),
            )
        else:
            print(f"Tests ran OK for workflow definitions in project {project.name}")
    return wf_defs_info
