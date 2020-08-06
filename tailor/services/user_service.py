from .client import client
from ..models import UserModel
from ..exceptions import ApiResponseError
from typing import List


def get_user() -> UserModel:
    resp = client.get('user/profile')
    if resp.status_code == 200:
        return UserModel.from_dict(resp.json())
    else:
        raise ApiResponseError(f'Unexpected API response: {str(resp)}')
