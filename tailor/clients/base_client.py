from httpx import Client
from tailor.config import API_BASE_URL, AUTH_KEY
from .auth import TailorAuth


class BaseClient(Client):
    def __init__(self):
        super().__init__(base_url=API_BASE_URL, auth=TailorAuth(AUTH_KEY))
