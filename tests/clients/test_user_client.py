from unittest.mock import patch
from tailor.models import User
from tailor.clients import UserClient
from ..mock_data import user_dict


mock_user = User.parse_obj(user_dict)


@patch.object(UserClient, "get_current_user", return_value=mock_user)
def test_get_current_user(get_current_user):
    assert get_current_user() == mock_user
