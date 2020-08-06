from tailor.models import UserModel
from .mock_data import user_dict


def test_user_model():
    user = UserModel.from_dict(user_dict)
    serialized = user.to_dict()
    deserialized = UserModel.from_dict(serialized)

    assert user == deserialized
