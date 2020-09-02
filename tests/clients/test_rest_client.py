from tailor.clients import RestClient

from ..data import *
from tailor.models import *


def test_get_projects(httpx_mock):
    httpx_mock.add_response(json=data_projects)
    with RestClient() as client:
        models = client.get_projects()
        for i, model in enumerate(models):
            assert isinstance(model, Project)
            assert model == Project(**data_projects[i])


def test_get_project(httpx_mock):
    httpx_mock.add_response(json=data_project)
    with RestClient() as client:
        model = client.get_project("702d688e-972d-4580")
        assert isinstance(model, Project)
        assert model == Project(**data_project)


def test_new_fileset(httpx_mock):
    project_id = 'a_project_id'
    httpx_mock.add_response(json=data_empty_fileset)
    with RestClient() as client:
        model = client.new_fileset(project_id)
    assert isinstance(model, FileSet)
    assert model == FileSet(**data_empty_fileset)


def test_get_download_urls_empty_payload(httpx_mock):
    project_id = 'a_project_id'
    fileset_id = 'a_filset_id'
    fileset_download = FileSetDownload()
    httpx_mock.add_response(json=data_empty_fileset)
    with RestClient() as client:
        model = client.get_download_urls(project_id, fileset_id, fileset_download)
    assert isinstance(model, FileSet)
    assert model == FileSet(**data_empty_fileset)


# TODO:
#   test_get_upload_urls
#   test_get_download_urls