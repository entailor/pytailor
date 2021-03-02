import httpx
from pytailor.models import *
from pytailor.config import (
    API_BASE_URL,
    SYNC_REQUEST_TIMEOUT,
    SYNC_CONNECT_TIMEOUT,
)
from .auth import TailorAuth


class RestClient(httpx.Client):
    def __init__(self):
        timeout = httpx.Timeout(
            timeout=SYNC_REQUEST_TIMEOUT, connect=SYNC_CONNECT_TIMEOUT
        )
        super().__init__(
            base_url=API_BASE_URL, auth=TailorAuth(), timeout=timeout
        )

    # accounts

    def get_accounts(self) -> List[Account]:
        url = "accounts"
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return [Account.parse_obj(obj) for obj in response.json()]
        else:
            response.raise_for_status()

    # projects

    def get_projects(self) -> List[Project]:
        url = "projects"
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return [Project.parse_obj(obj) for obj in response.json()]
        else:
            response.raise_for_status()

    def get_project(self, project_id: str) -> Project:
        url = f"projects/{project_id}"
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return Project.parse_obj(response.json())
        else:
            response.raise_for_status()

    # filesets

    def new_fileset(self, project_id: str) -> FileSet:
        url = f"projects/{project_id}/filesets"
        response = self.post(url)
        if response.status_code == httpx.codes.OK:
            return FileSet.parse_obj(response.json())
        else:
            response.raise_for_status()

    def get_download_urls(
        self, project_id: str, fileset_id: str, fileset_download: FileSetDownload
    ) -> FileSet:
        url = f"projects/{project_id}/filesets/{fileset_id}/downloads"
        response = self.post(url, data=fileset_download.json())
        if response.status_code == httpx.codes.OK:
            return FileSet.parse_obj(response.json())
        else:
            response.raise_for_status()

    def get_upload_urls(
        self, project_id: str, fileset_id: str, fileset_upload: FileSetUpload
    ) -> FileSet:
        url = f"projects/{project_id}/filesets/{fileset_id}/uploads"
        response = self.post(url, data=fileset_upload.json())
        if response.status_code == httpx.codes.OK:
            return FileSet.parse_obj(response.json())
        else:
            response.raise_for_status()

    # workflows

    def get_workflow(self, project_id: str, wf_id: str) -> Workflow:
        url = f"projects/{project_id}/workflows/{wf_id}"
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return Workflow.parse_obj(response.json())
        else:
            response.raise_for_status()

    def get_workflows(self, project_id: str) -> List[Workflow]:
        url = f"projects/{project_id}/workflows"
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return [Workflow.parse_obj(obj) for obj in response.json()]
        else:
            response.raise_for_status()

    def new_workflow(self, project_id: str, create_data: WorkflowCreate) -> Workflow:
        url = f"projects/{project_id}/workflows"
        response = self.post(url, data=create_data.json())
        if response.status_code == httpx.codes.OK:
            return Workflow.parse_obj(response.json())
        else:
            response.raise_for_status()

    def delete_workflow(self, project_id: str, wf_id: str):
        url = f"projects/{project_id}/workflows/{wf_id}"
        response = self.delete(url)
        if response.status_code == httpx.codes.OK:
            return response
        else:
            response.raise_for_status()

    # workflow definitions

    def get_workflow_definition_project(
        self, project_id: str, wf_def_id: int
    ) -> WorkflowDefinition:
        url = f"projects/{project_id}/workflow_definitions/{wf_def_id}"
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return WorkflowDefinition.parse_obj(response.json())
        else:
            response.raise_for_status()

    def get_workflow_definition_summaries_project(
        self, project_id: str
    ) -> List[WorkflowDefinitionSummary]:
        url = f"projects/{project_id}/workflow_definitions"
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return [WorkflowDefinitionSummary.parse_obj(obj) for obj in response.json()]
        else:
            response.raise_for_status()

    def new_workflow_definition(
        self, account_id, create_data: WorkflowDefinitionCreate
    ) -> WorkflowDefinition:
        url = f"accounts/{account_id}/workflow_definitions"
        response = self.post(url, data=create_data.json())
        if response.status_code == httpx.codes.OK:
            return WorkflowDefinition.parse_obj(response.json())
        else:
            response.raise_for_status()

    def update_workflow_definitions_for_project(
        self, project_id: str, permission_change: PermissionChange
    ) -> PermissionList:
        url = f"/projects/{project_id}/permissions/workflow-definitions"
        response = self.post(url, data=permission_change.json())
        if response.status_code == httpx.codes.OK:
            return PermissionList.parse_obj(response.json())
        else:
            response.raise_for_status()

    # task checkout/checkin

    def checkout_task(self, checkout_query: TaskCheckout) -> TaskExecutionData:
        url = f"tasks/checkouts"
        response = self.post(url, data=checkout_query.json())
        if response.status_code == httpx.codes.OK:
            return TaskExecutionData.parse_obj(response.json())
        else:
            response.raise_for_status()

    def checkin_task(self, task_update: TaskUpdate) -> TaskExecutionData:
        url = f"tasks/checkins"
        response = self.post(url, data=task_update.json())
        if response.status_code == httpx.codes.OK:
            return TaskExecutionData.parse_obj(response.json())
        else:
            response.raise_for_status()

    def perform_task_operation(self, wf_id: str, project_id: str, task_id: str,
                               task_operation: TaskOperation) -> TaskSummary:
        url = f"projects/{project_id}/workflows/{wf_id}/tasks/{task_id}/operations"
        response = self.post(url, data=task_operation.json())
        if response.status_code == httpx.codes.OK:
            return TaskSummary.parse_obj(response.json())
        else:
            response.raise_for_status()

    def get_task_result(self, processing_id: str) -> TaskExecutionData:
        url = f"tasks/results/{processing_id}"
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return TaskExecutionData.parse_obj(response.json())
        else:
            response.raise_for_status()
