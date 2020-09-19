import httpx
from pytailor.models import *
from pytailor.config import API_BASE_URL, AUTH_KEY
from .auth import TailorAuth


class RestClient(httpx.Client):

    def __init__(self):
        super().__init__(base_url=API_BASE_URL, auth=TailorAuth(AUTH_KEY),
                         timeout=15.0)

    # accounts

    def get_accounts(self) -> List[Account]:
        url = 'accounts'
        response = self.get(url)
        accounts = [Account.parse_obj(obj) for obj in response.json()]
        return accounts

    # projects

    def get_projects(self) -> List[Project]:
        url = 'projects'
        response = self.get(url)
        projects = [Project.parse_obj(obj) for obj in response.json()]
        return projects

    def get_project(self, project_id: str) -> Project:
        url = f'projects/{project_id}'
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return Project.parse_obj(response.json())
        else:
            response.raise_for_status()

    # filesets

    def new_fileset(self, project_id: str) -> FileSet:
        url = f'projects/{project_id}/filesets'
        response = self.post(url)
        if response.status_code == httpx.codes.OK:
            return FileSet.parse_obj(response.json())
        else:
            response.raise_for_status()

    def get_download_urls(self,
                          project_id: str,
                          fileset_id: str,
                          fileset_download: FileSetDownload
                          ) -> FileSet:
        url = f'projects/{project_id}/filesets/{fileset_id}/downloads'
        response = self.post(url, data=fileset_download.json())
        if response.status_code == httpx.codes.OK:
            return FileSet.parse_obj(response.json())
        else:
            response.raise_for_status()

    def get_upload_urls(self,
                        project_id: str,
                        fileset_id: str,
                        fileset_upload: FileSetUpload
                        ) -> FileSet:
        url = f'projects/{project_id}/filesets/{fileset_id}/uploads'
        response = self.post(url, data=fileset_upload.json())
        if response.status_code == httpx.codes.OK:
            return FileSet.parse_obj(response.json())
        else:
            response.raise_for_status()

    # workflows

    def get_workflow(self, project_id: str, wf_id: str) -> Workflow:
        url = f'projects/{project_id}/workflows/{wf_id}'
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return Workflow.parse_obj(response.json())
        else:
            response.raise_for_status()

    def new_workflow(self, project_id: str,
                     create_data: WorkflowCreate) -> Workflow:
        url = f'projects/{project_id}/workflows'
        response = self.post(url, data=create_data.json())
        if response.status_code == httpx.codes.OK:
            return Workflow.parse_obj(response.json())
        else:
            response.raise_for_status()

    # workflow definitions

    def get_workflow_definition_project(self, project_id: str, wf_def_id: int
                                        ) -> WorkflowDefinition:
        url = f'projects/{project_id}/workflow_definitions/{wf_def_id}'
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return WorkflowDefinition.parse_obj(response.json())
        else:
            response.raise_for_status()

    def get_workflow_definition_summaries_project(
            self, project_id: str) -> List[WorkflowDefinitionSummary]:
        url = f'projects/{project_id}/workflow_definitions'
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return [WorkflowDefinitionSummary.parse_obj(obj) for obj in response.json()]
        else:
            response.raise_for_status()

    def new_workflow_definition(self, account_id, create_data: WorkflowDefinitionCreate):
        url = f'accounts/{account_id}/workflow_definitions'
        response = self.post(url, data=create_data.json())
        if response.status_code == httpx.codes.OK:
            return Workflow.parse_obj(response.json())
        else:
            response.raise_for_status()

    # task checkout/checkin

    def checkout_task(self, checkout_query: TaskCheckout) -> TaskExecutionData:
        url = f'tasks/checkouts'
        response = self.post(url, data=checkout_query.json())
        if response.status_code == httpx.codes.OK:
            return TaskExecutionData.parse_obj(response.json())
        else:
            response.raise_for_status()

    def checkin_task(self, task_update: TaskUpdate) -> TaskExecutionData:
        url = f'tasks/checkins'
        response = self.post(url, data=task_update.json())
        if response.status_code == httpx.codes.OK:
            return TaskExecutionData.parse_obj(response.json())
        else:
            response.raise_for_status()