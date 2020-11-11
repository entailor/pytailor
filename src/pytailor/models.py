# generated by datamodel-codegen:
#   filename:  openapi.json
#   timestamp: 2020-11-11T07:22:43+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Account(BaseModel):
    id: Optional[str] = Field(None, title="unique identifier")
    organization_name: Optional[str] = Field(None, title="organization name")
    organization_id: Optional[str] = Field(
        None, title="the official registration number of the organization"
    )
    projects: Optional[List[str]] = Field(
        None, title="the projects owned by this account, by id"
    )
    users: Optional[List[str]] = Field(
        None, title="the users who are a member of this account, by id"
    )
    admin_users: Optional[List[str]] = Field(
        None, title="the users who are a account admins of this account, by id"
    )
    workflow_definitions_owned: Optional[List[str]] = Field(
        None, title="the workflow definitions owned by this account, by id"
    )
    workflow_definitions_subscriptions: Optional[List[str]] = Field(
        None, title="the workflow definitions subscribed to by this account, by id"
    )


class ApiKey(BaseModel):
    api_worker_id: str = Field(..., title="Api Worker Id")
    api_secret_key: str = Field(..., title="Api Secret Key")


class Context(BaseModel):
    inputs: Optional[Dict[str, Any]] = Field(None, title="Scoped inputs")
    outputs: Optional[Dict[str, Any]] = Field(None, title="Scoped outputs")
    files: Optional[Dict[str, Any]] = Field(None, title="File list by tag")


class FileSetDownload(BaseModel):
    task_id: Optional[str] = Field(None, title="Task to scope the fileset against")
    tags: Optional[List[str]] = Field(None, title="List of tags to download files for")


class FileSetLink(BaseModel):
    filename: str = Field(..., title="Filename")
    url: str = Field(..., title="Url")
    size: Optional[str] = Field(None, title="Size")


class FileSetLinks(BaseModel):
    tag_name: Optional[str] = Field(None, title="The tag name of the files")
    links: Optional[List[FileSetLink]] = Field(None, title="The files")


class Tags(BaseModel):
    __root__: List[str]


class FileSetUpload(BaseModel):
    task_id: Optional[str] = Field(None, title="Task to scope the fileset against")
    tags: Dict[str, Tags] = Field(
        ..., title="Dict of tags, each containing a list of file names"
    )


class PermissionChange(BaseModel):
    add: Optional[List[str]] = Field([], title="Ids to add")
    delete: Optional[List[str]] = Field([], title="Ids to remove")


class PermissionList(BaseModel):
    __root__: List[str] = Field(..., title="PermissionList")


class ProcessingStatus(Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    FAILED = "FAILED"


class StorageType(Enum):
    AZURE_BLOB_CONTAINER = "AZURE_BLOB_CONTAINER"
    LOCAL_FILESYSTEM = "LOCAL_FILESYSTEM"
    S3_BUCKET = "S3_BUCKET"


class TaskCheckout(BaseModel):
    worker_capabilities: Optional[List[str]] = Field(
        None, title="The worker's task capabilities"
    )
    worker_id: Optional[str] = Field(None, title="The unique id of the worker")
    worker_name: Optional[str] = Field(
        None, title="A human-friendly name describing the worker"
    )
    projects: Optional[List[str]] = Field(
        None, title="(Optional) limit tasks to these projects, by id"
    )
    workflow_definitions: Optional[List[str]] = Field(
        None,
        title="(Optional) limit tasks to those origination from these workflow definitions, by id",
    )
    workflows: Optional[List[str]] = Field(
        None, title="(Optional) limit tasks to these workflows, by id"
    )


class Context1(Context):
    pass


class TaskExecutionData(BaseModel):
    run_id: Optional[str] = Field(
        None, title="The current Task Run id, if it is running"
    )
    task_id: Optional[str] = Field(None, title="The task's id")
    definition: Optional[Dict[str, Any]] = Field(None, title="The task's definition")
    context: Optional[Context1] = Field(None, title="The task's context")
    fileset_id: Optional[str] = Field(
        None, title="Reference to the Workflow's fileset object"
    )
    project_id: Optional[str] = Field(None, title="Reference to the Workflow's project")
    processing_status: Optional[ProcessingStatus] = Field(
        "COMPLETED", title="Status of the checkout/checkin"
    )
    processing_id: Optional[str] = Field(
        None,
        description="Use the processing id to retrieve PENDING results from /task/pending-results/{id}",
        title="Processing id",
    )
    processing_msg: Optional[str] = Field(
        None, title="A message with info about the processing result"
    )


class TaskOperationType(Enum):
    RESET = "RESET"


class TaskState(Enum):
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"
    WAITING = "WAITING"
    READY = "READY"
    RESERVED = "RESERVED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"


class TaskSummary(BaseModel):
    id: Optional[str] = Field(None, title="unique identifier of the task")
    name: Optional[str] = Field(None, title="non-unique name of the task")
    updated_utc: Optional[str] = Field(
        None, title="timestamp of the latest change, in ISO-8601 datetime format"
    )
    state: Optional[TaskState] = Field(None, title="current state of the task")


class TaskUpdate(BaseModel):
    task_id: Optional[str] = Field(None, title="The identifier of the task")
    run_id: Optional[str] = Field(None, title="The identifier of the task run")
    state: Optional[TaskState] = Field(None, title="The updated state of the task run")
    outputs: Optional[Dict[str, Any]] = Field(
        None, title="The updated outputs of the task run"
    )
    failure_summary: Optional[str] = Field(None, title="A summary of the failure")
    failure_detail: Optional[str] = Field(
        None, title="Detailed information about the failure"
    )
    run_dir: Optional[str] = Field(
        None,
        title="The location on the Worker's filesystem for the current task run. Mandatory on first check in.",
    )
    perform_branching: Optional[bool] = Field(
        False, title="Signal to the backend to perform branching"
    )


class User(BaseModel):
    username: Optional[str] = Field(None, title="unique username")
    id: Optional[str] = Field(None, title="unique identifier")
    accounts: Optional[List[str]] = Field(
        None, title="the accounts the user has access to, by id"
    )
    projects: Optional[List[str]] = Field(
        None, title="the projects the user has access to, by id"
    )
    given_name: Optional[str] = Field(None, title="the user's given name")
    family_name: Optional[str] = Field(None, title="the user's family name")
    email: Optional[str] = Field(None, title="the user's email address")
    phone_number: Optional[str] = Field(None, title="the user's phone number")


class UserSummary(BaseModel):
    username: Optional[str] = Field(None, title="unique username")
    id: Optional[str] = Field(None, title="unique identifier")
    accounts: Optional[List[str]] = Field(
        None, title="the accounts the user has access to, by id"
    )
    projects: Optional[List[str]] = Field(
        None, title="the projects the user has access to, by id"
    )


class ValidationError(BaseModel):
    loc: List[str] = Field(..., title="Location")
    msg: str = Field(..., title="Message")
    type: str = Field(..., title="Error Type")


class WorkflowCreate(BaseModel):
    from_definition_id: Optional[str] = Field(
        None, title="(Optional) the workflow definition to base this Workflow on"
    )
    dag: Optional[Dict[str, Any]] = Field(
        None, title="(Optional) The DAG specification as JSON"
    )
    name: Optional[str] = Field(None, title="The name selected for this Workflow")
    inputs: Optional[Dict[str, Any]] = Field(
        None, title="(Optional) the inputs to the Workflow"
    )
    worker_name_restriction: Optional[str] = Field(
        None, title="(Optional) the name of the one Worker who should run this workflow"
    )
    fileset_id: Optional[str] = Field(
        None,
        title="(Optional) use input files from the specified FileSet. If not specified, a new, initially empty, FileSet will be created",
    )


class WorkflowDefinition(BaseModel):
    id: Optional[str] = Field(None, title="unique ID of the workflow definition")
    name: Optional[str] = Field(
        None, title="non-unique name of the workflow definition"
    )
    description: Optional[str] = Field(None, title="description of the workflow")
    dag: Optional[Dict[str, Any]] = Field(None, title="the dag as json")
    inputs_schema: Optional[Dict[str, Any]] = Field(
        None, title="the inputs schema as json"
    )
    outputs_schema: Optional[Dict[str, Any]] = Field(
        None, title="the outputs schema as json"
    )
    files_schema: Optional[Dict[str, Any]] = Field(
        None, title="the files schema as json"
    )
    owner_id: Optional[str] = Field(
        None, title="the account that owns this workflow definition, by id"
    )
    subscribers: Optional[List[str]] = Field(
        None, title="the accounts that subscribes to this workflow definition, by id"
    )
    created_by_user: Optional[str] = Field(None, title="the uuid of the creating user")
    created_on: Optional[str] = Field(
        None, title="the date and time this workflow definition was created"
    )


class WorkflowDefinitionCreate(BaseModel):
    dag: Optional[Dict[str, Any]] = Field(None, title="The DAG definition as JSON")
    inputs_schema: Optional[Dict[str, Any]] = Field(
        None, title="(Optional) The inputs schema specification as JSON"
    )
    outputs_schema: Optional[Dict[str, Any]] = Field(
        None, title="(Optional) The outputs schema specification as JSON"
    )
    files_schema: Optional[Dict[str, Any]] = Field(
        None, title="(Optional) The files schema specification as JSON"
    )
    name: Optional[str] = Field(None, title="The name selected for this Workflow")
    description: Optional[str] = Field(
        None,
        title="The description of this workflow definition, in Markdown format or plain text",
    )


class WorkflowDefinitionSummary(BaseModel):
    id: Optional[str] = Field(None, title="unique ID of the workflow definition")
    name: Optional[str] = Field(
        None, title="non-unique name of the workflow definition"
    )
    description: Optional[str] = Field(None, title="description of the workflow")


class WorkflowSummary(BaseModel):
    id: Optional[str] = Field(None, title="unique ID of the workflow")
    name: Optional[str] = Field(None, title="non-unique name of the workflow")
    project_id: Optional[str] = Field(None, title="project that owns this workflow")
    updated_utc: Optional[str] = Field(
        None, title="timestamp of the latest change, in ISO-8601 datetime format"
    )
    user_id: Optional[str] = Field(None, title="user that created this workflow")
    state: Optional[str] = Field(
        None, title="current aggregated state of the workflow's tasks"
    )
    from_definition_id: Optional[str] = Field(
        None, title="The workflow definition this Workflow is based on"
    )


class WorkflowTask(BaseModel):
    id: Optional[str] = Field(None, title="Task id")
    name: Optional[str] = Field(None, title="Task name")
    type: Optional[str] = Field(None, title="Task type")


class FileSet(BaseModel):
    id: Optional[str] = Field(None, title="unique identifier")
    tags: Optional[List[FileSetLinks]] = Field(None, title="File links")
    size: Optional[str] = Field(None, title="Total size of files in fileset")


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = Field(None, title="Detail")


class Project(BaseModel):
    id: Optional[str] = Field(None, title="unique identifier")
    name: Optional[str] = Field(None, title="project name")
    account_id: Optional[str] = Field(None, title="the project owner account, by id")
    storage_type: Optional[StorageType] = Field(None, title="File storage type")
    storage_identifier: Optional[str] = Field(
        None, title="Name or equivalent within the given storage_type"
    )
    external_reference: Optional[str] = Field(
        None, title="a reference number or code this project uses in other systems"
    )
    available_workflow_definitions: Optional[List[str]] = Field(
        [], title="the workflow definitions this project can use, by id"
    )
    users: Optional[List[str]] = Field(
        [], title="the users who are a member of this account, by id"
    )


class TaskOperation(BaseModel):
    type: Optional[TaskOperationType] = Field(
        None, title="The type of operation to be performed"
    )


class TaskRun(BaseModel):
    state: Optional[TaskState] = Field(None, title="state of the task run")
    ended_utc: Optional[str] = Field(
        None, title="timestamp of when the workflow ended, in ISO-8601 datetime format"
    )
    traceback: Optional[List[str]] = Field(None, title="detailed error message")
    traceback_raw: Optional[str] = Field(
        None, title="unformatted, detailed error message"
    )
    error_message: Optional[str] = Field(None, title="summarized error message")


class Workflow(BaseModel):
    id: Optional[str] = Field(None, title="unique ID of the workflow")
    name: Optional[str] = Field(None, title="non-unique name of the workflow")
    project_id: Optional[str] = Field(None, title="project that owns this workflow")
    updated_utc: Optional[str] = Field(
        None, title="timestamp of the latest change, in ISO-8601 datetime format"
    )
    user_id: Optional[str] = Field(None, title="user that created this workflow")
    state: Optional[str] = Field(
        None, title="current aggregated state of the workflow's tasks"
    )
    from_definition_id: Optional[str] = Field(
        None, title="The workflow definition this Workflow is based on"
    )
    created_utc: Optional[str] = Field(
        None,
        title="timestamp of when the workflow was created, in ISO-8601 datetime format",
    )
    task_links: Optional[Dict[str, Any]] = Field(
        None, title="links between tasks in the workflow"
    )
    root_tasks: Optional[List[str]] = Field(None, title="root task(s) of the workflow")
    task_states: Optional[Dict[str, Any]] = Field(
        None, title="current state of each task"
    )
    fileset_id: Optional[str] = Field(
        None, title="reference to the Workflow's fileset object"
    )
    dag: Optional[Dict[str, Any]] = Field(None, title="The Workflow's dag")
    inputs: Optional[Dict[str, Any]] = Field(None, title="The Workflow's input")
    outputs: Optional[Dict[str, Any]] = Field(None, title="The Workflow's output")
    files: Optional[Dict[str, Any]] = Field(None, title="The Workflow's files")
    tasks: Optional[List[WorkflowTask]] = Field(None, title="The Workflow's output")


class Task(BaseModel):
    id: Optional[str] = Field(None, title="unique identifier of the task")
    name: Optional[str] = Field(None, title="non-unique name of the task")
    updated_utc: Optional[str] = Field(
        None, title="timestamp of the latest change, in ISO-8601 datetime format"
    )
    state: Optional[TaskState] = Field(None, title="current state of the task")
    created_utc: Optional[str] = Field(
        None,
        title="timestamp of when the task was created, in ISO-8601 datetime format",
    )
    runs: Optional[List[TaskRun]] = Field(
        None, title="list of results from running this task"
    )
    definition: Optional[Dict[str, Any]] = Field(None, title="definition of the task")
    inputs: Optional[Dict[str, Any]] = Field(
        None, title="Contextualized inputs for task"
    )
    outputs: Optional[Dict[str, Any]] = Field(
        None, title="Contextualized outputs for task"
    )
    files: Optional[Dict[str, Any]] = Field(None, title="Contextualized files for task")
