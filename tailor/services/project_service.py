from .client import client
from ..models import ProjectModel
from ..exceptions import ApiResponseError
import httpx


def get_project_by_uuid(uuid) -> ProjectModel:
    resp = client.get(f'projects/{uuid}')
    if resp.status_code == httpx.codes.OK:
        return ProjectModel.from_dict(resp.json())
    else:
        raise ApiResponseError(f'Unexpected API response: {str(resp)}')
