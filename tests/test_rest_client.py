from tailor.clients import RestClient

from .data import *


def test_get_projects(httpx_mock):
    from tailor.models import Project

    httpx_mock.add_response(json=data_projects)
    with RestClient() as client:
        models = client.get_projects()
        for i, model in enumerate(models):
            assert isinstance(model, Project)
            assert model == Project(**data_projects[i])


def test_get_project(httpx_mock):
    from tailor.models import Project
    httpx_mock.add_response(json=data_project)
    with RestClient() as client:
        model = client.get_project("702d688e-972d-4580")
        assert isinstance(model, Project)
        assert model == Project(**data_project)


def test_get_project_unknown_id(httpx_mock):
    # backend currently gives a 403 on unknown project_id
    httpx_mock.add_response(status_code=403)
    with RestClient() as client:
        model = client.get_project("a_non_existing_id")
        assert model is None


def test_new_fileset(httpx_mock):
    project_id = 'a_project_id'

    from tailor.models import FileSet
    httpx_mock.add_response(json=data_empty_fileset)
    with RestClient() as client:
        model = client.new_fileset(project_id)
        assert isinstance(model, FileSet)
        assert model == FileSet(**data_empty_fileset)
