from unittest.mock import patch
import pytest

from tailor import Project
from tailor.models import Project as ProjectModel
from tailor.exceptions import BackendResponseError
from ..data import *

# an empty FileSet model to use in tests
model_obj = ProjectModel(**data_project)
model_objs = [ProjectModel(**data) for data in data_projects]


@patch('tailor.clients.RestClient.get_project', return_value=model_obj)
def test_get_project_from_id(mocked_method):
    obj = Project(model_obj.id)
    assert obj.id == model_obj.id
    assert obj.name == model_obj.name
    mocked_method.assert_called_once()


def test_get_project_from_bad_id(httpx_mock):
    httpx_mock.add_response(status_code=403)
    with pytest.raises(BackendResponseError):
        Project(model_obj.id)


@patch('tailor.clients.RestClient.get_projects', return_value=model_objs)
@patch('tailor.clients.RestClient.get_project', return_value=model_obj)
def test_get_project_from_name(mocked_method1, mocked_method2):
    obj = Project.from_name(model_obj.name)
    assert obj.id == model_obj.id
    assert obj.name == model_obj.name
    mocked_method1.assert_called_once()
    mocked_method2.assert_called_once()


def test_get_project_from_bad_name(httpx_mock):
    httpx_mock.add_response(json=data_projects)
    with pytest.raises(ValueError):
        Project.from_name('Non-existing')


@patch('tailor.clients.RestClient.get_projects', return_value=model_objs)
def test_get_project_from_bad_name_alt_mocking(mocked_method):
    with pytest.raises(ValueError):
        Project.from_name('Non-existing')
    mocked_method.assert_called_once()
