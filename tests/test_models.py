from tailor.models import UserModel, ProjectModel
from .mock_data import user_dict, project_dict


def test_user_model():
    user = UserModel.from_dict(user_dict)
    serialized = user.to_dict()
    deserialized = UserModel.from_dict(serialized)

    assert user == deserialized


def test_project_model():
    project = ProjectModel.from_dict(project_dict)
    serialized = project.to_dict()
    deserialized = ProjectModel.from_dict(serialized)

    assert project == deserialized
