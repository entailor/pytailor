from typing import List
import httpx
from pydantic import BaseModel, ValidationError
from tailor.models import Project, User, Workflow
from tailor.config import API_BASE_URL, AUTH_KEY
from .auth import TailorAuth


class RestClient(httpx.Client):

    def __init__(self):
        super().__init__(base_url=API_BASE_URL, auth=TailorAuth(AUTH_KEY))

    # TODO: requests to the backend should be centralized?, e.g.:
    # def __get(self, url: str) -> httpx.Response:
    #     """Do a GET request with error handling"""
    #     try:
    #         response = self.get(url)
    #         response.raise_for_status()
    #     except httpx.RequestError as exc:
    #         print(f"An error occurred while requesting {exc.request.url!r}.")
    #         raise
    #     except httpx.HTTPStatusError as exc:
    #         print(f'Error response {exc.response.status_code} while requesting '
    #               f'{exc.request.url!r}.')
    #         raise
    #     return response

    # TODO: model creation should be centralized?, e.g.:
    # def __get_model_instance(self, url: str, model_cls) -> BaseModel:
    #     response = self.__get(url)
    #     try:
    #         return model_cls.parse_obj(response.json())
    #     except ValidationError as exc:
    #         print(exc)
    #         raise

    # projects

    def get_projects(self) -> List[Project]:
        url = 'projects'
        request = self.get(url)
        projects = [Project.parse_obj(obj) for obj in request.json()]
        return projects

    def get_project(self, project_uuid: str) -> Project:
        url = f'projects/{project_uuid}'
        request = self.get(url)
        project = Project.parse_obj(request.json())
        return project

    # users

    def get_current_user(self) -> User:
        url = 'profile'
        request = self.get(url)
        user = User.parse_obj(request.json())
        return user

    def get_project_users(self, project_uuid: str) -> List[User]:
        url = f'projects/{project_uuid}/users'
        request = self.get(url)
        project_users = [User.parse_obj(obj) for obj in request.json()]
        return project_users

    # workflows

    def get_workflow(self, project_uuid: str, wf_id: int) -> Workflow:
        url = f'projects/{project_uuid}/workflows{wf_id}'
        request = self.get(url)
        return Workflow.parse_obj(request.json())
