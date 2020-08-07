from .client import client
from ..models import UserModel
from ..exceptions import ApiResponseError
import httpx


def get_user() -> UserModel:
    resp = client.get('user/profile')
    if resp.status_code == httpx.codes.OK:
        return UserModel.from_dict(resp.json())
    else:
        raise ApiResponseError(f'Unexpected API response: {str(resp)}')
