import httpx
from tailor.models import *
from tailor.config import API_BASE_URL, AUTH_KEY
from .auth import TailorAuth


class RestClient(httpx.Client):

    def __init__(self):
        super().__init__(base_url=API_BASE_URL, auth=TailorAuth(AUTH_KEY))

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

    def get_workflow(self, project_id: str, wf_id: int) -> Workflow:
        url = f'projects/{project_id}/workflows/{wf_id}'
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return Workflow.parse_obj(response.json())
        else:
            response.raise_for_status()

    def create_workflow(self, project_id: str,
                        create_data: WorkflowCreate) -> Workflow:
        url = f'projects/{project_id}/workflows'
        response = self.post(url, data=create_data.json())
        if response.status_code == httpx.codes.OK:
            return Workflow.parse_obj(response.json())
        else:
            response.raise_for_status()