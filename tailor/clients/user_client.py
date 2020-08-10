from httpx import Client
from pydantic import ValidationError

from tailor.models import User, UserSummary
from tailor.config import API_BASE_URL, AUTH_KEY
from .auth import TailorAuth
# from urllib.parse import urljoin


class UserClient(Client):
    def __init__(self):
        super().__init__(base_url=API_BASE_URL, auth=TailorAuth(AUTH_KEY))

    def get_current_user(self):
        request = self.get('profile')

        try:
            user = User.parse_obj(request.json())
        except ValidationError:
            print('ValidationError...')

        return user
