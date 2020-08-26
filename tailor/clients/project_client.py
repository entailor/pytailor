# from pydantic import ValidationError
from typing import List
from tailor.models import Project
from .base_client import BaseClient


class ProjectClient(BaseClient):

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
