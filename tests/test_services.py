from unittest.mock import Mock, patch
import pytest
from tailor.services.user_service import get_user
from tailor.models import UserModel
from tailor.exceptions import ApiResponseError
from .mock_data import user_dict


@patch('tailor.services.user_service.client.get')
def test_get_user_ok(mock_get):

    mock_get.return_value = Mock(status_code=200)
    mock_get.return_value.json.return_value = user_dict

    user1 = UserModel.from_dict(user_dict)
    user2 = get_user()

    assert user1 == user2


@patch('tailor.services.user_service.client.get')
def test_get_user_not_ok(mock_get):

    mock_get.return_value = Mock(status_code=404)
    with pytest.raises(ApiResponseError):
        get_user()
