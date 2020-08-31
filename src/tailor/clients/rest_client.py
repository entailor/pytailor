from typing import List, Optional
import httpx
from pydantic import BaseModel, ValidationError
from tailor.models import Project, User, Workflow, FileSet, FileSetDownload
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

    def get_project(self, project_id: str) -> Optional[Project]:
        url = f'projects/{project_id}'
        response = self.get(url)
        if response.status_code == httpx.codes.OK:
            return Project.parse_obj(response.json())
        else:
            return None

    # users

    def get_current_user(self) -> User:
        url = 'profile'
        response = self.get(url)
        user = User.parse_obj(response.json())
        return user

    def get_project_users(self, project_id: str) -> List[User]:
        url = f'projects/{project_id}/users'
        response = self.get(url)
        project_users = [User.parse_obj(obj) for obj in response.json()]
        return project_users

    # workflows

    def get_workflow(self, project_uuid: str, wf_id: int) -> Workflow:
        url = f'projects/{project_uuid}/workflows/{wf_id}'
        response = self.get(url)
        return Workflow.parse_obj(response.json())

    # filesets

    def new_fileset(self, project_id: str) -> Optional[FileSet]:
        url = f'projects/{project_id}/filesets'
        print(url)
        response = self.post(url)
        if response.status_code == httpx.codes.OK:
            return FileSet.parse_obj(response.json())
        else:
            return None

    def get_download_urls(self,
                          project_id: str,
                          fileset_id: str,
                          fileset_download: FileSetDownload
                          ) -> Optional[FileSet]:
        url = f'projects/{project_id}/filesets/{fileset_id}'
        response = self.post(url, data=fileset_download.json())
        if response.status_code == httpx.codes.OK:
            return FileSet.parse_obj(response.json())
        else:
            return None
