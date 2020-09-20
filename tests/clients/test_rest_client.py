from pytailor.clients import RestClient

from ..data import *
from pytailor.models import *


def test_get_accounts(httpx_mock):
    httpx_mock.add_response(json=data_accounts)
    with RestClient() as client:
        models = client.get_accounts()
        for i, model in enumerate(models):
            assert isinstance(model, Account)
            assert model == Account(**data_accounts[i])


def test_get_projects(httpx_mock):
    httpx_mock.add_response(json=data_projects)
    with RestClient() as client:
        models = client.get_projects()
        for i, model in enumerate(models):
            assert isinstance(model, Project)
            assert model == Project(**data_projects[i])


def test_get_project(httpx_mock):
    project_id = "a_project_id"
    httpx_mock.add_response(json=data_project)
    with RestClient() as client:
        model = client.get_project(project_id)
        assert isinstance(model, Project)
        assert model == Project(**data_project)


def test_new_fileset(httpx_mock):
    project_id = "a_project_id"
    httpx_mock.add_response(json=data_empty_fileset)
    with RestClient() as client:
        model = client.new_fileset(project_id)
    assert isinstance(model, FileSet)
    assert model == FileSet(**data_empty_fileset)


def test_get_download_urls_empty_payload(httpx_mock):
    project_id = "a_project_id"
    fileset_id = "a_filset_id"
    fileset_download = FileSetDownload()
    httpx_mock.add_response(json=data_empty_fileset)
    with RestClient() as client:
        model = client.get_download_urls(project_id, fileset_id, fileset_download)
    assert isinstance(model, FileSet)
    assert model == FileSet(**data_empty_fileset)


def test_get_download_urls(httpx_mock):
    project_id = "a_project_id"
    fileset_id = "a_filset_id"
    fileset_download = FileSetDownload(**data_fileset_download)
    httpx_mock.add_response(json=data_fileset)
    with RestClient() as client:
        model = client.get_download_urls(project_id, fileset_id, fileset_download)
    assert isinstance(model, FileSet)
    assert model == FileSet(**data_fileset)


def test_get_upload_urls(httpx_mock):
    project_id = "a_project_id"
    fileset_id = "a_filset_id"
    fileset_upload = FileSetUpload(**data_fileset_upload)
    httpx_mock.add_response(json=data_fileset)
    with RestClient() as client:
        model = client.get_upload_urls(project_id, fileset_id, fileset_upload)
    assert isinstance(model, FileSet)
    assert model == FileSet(**data_fileset)


def test_get_workflow(httpx_mock):
    project_id = "a_project_id"
    workflow_id = "1"
    httpx_mock.add_response(json=data_workflow)
    with RestClient() as client:
        model = client.get_workflow(project_id, workflow_id)
        assert isinstance(model, Workflow)
        assert model == Workflow(**data_workflow)


def test_new_workflow_from_dag(httpx_mock):
    project_id = "a_project_id"
    workflow_create = WorkflowCreate(**data_workflow_create_dag)
    httpx_mock.add_response(json=data_workflow)
    with RestClient() as client:
        model = client.new_workflow(project_id, workflow_create)
    assert isinstance(model, Workflow)
    assert model == Workflow(**data_workflow)


def test_new_workflow_from_def(httpx_mock):
    pass
