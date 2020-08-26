from pydantic import ValidationError
from typing import List
from tailor.models import User
from .base_client import BaseClient


class UserClient(BaseClient):

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
