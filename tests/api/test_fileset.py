from unittest.mock import patch, Mock
import pytest

from tailor import FileSet
from tailor.models import FileSet as FileSetModel
from tailor.exceptions import BackendResponseError

from ..data import data_empty_fileset

# an empty FileSet model to use in tests
model_obj = FileSetModel(**data_empty_fileset)


@patch('tailor.clients.RestClient.new_fileset', return_value=model_obj)
def test_create_fileset(mocked_method):
    obj = FileSet(project=Mock())
    assert obj.id == model_obj.id
    mocked_method.assert_called_once()


@patch('tailor.clients.RestClient.get_download_urls', return_value=model_obj)
def test_get_existing_fileset(mocked_method):
    obj = FileSet(project=Mock(), fileset_id=model_obj.id)
    assert obj.id == model_obj.id
    mocked_method.assert_called_once()


def test_get_non_existing_fileset(httpx_mock):
    httpx_mock.add_response(status_code=404)
    with pytest.raises(BackendResponseError):
        FileSet(project=Mock(), fileset_id=model_obj.id)
