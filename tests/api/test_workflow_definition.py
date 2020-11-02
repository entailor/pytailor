from unittest.mock import patch, Mock
import pytest

from pytailor import WorkflowDefinition, DAG, Account, Workflow
from pytailor.models import WorkflowDefinition as WorkflowDefinitionModel
from pytailor.models import WorkflowDefinitionCreate
from pytailor.models import Account as AccountModel
from pytailor.exceptions import BackendResponseError
from ..data import dag_data, data_workflow


@pytest.fixture(scope='session', autouse=True)
def dag():
    return DAG.from_dict(dag_data)


def test_create_wf_def():
    wf_def = WorkflowDefinition(
        name=Mock(),
        description=Mock(),
        dag=dag
    )
    assert wf_def.dag == dag
    assert not wf_def.id


wf_def_model = WorkflowDefinitionModel(
        id='asdf',
        name='asdf',
        description='asdf',
        dag=DAG.from_dict(dag_data).to_dict()
    )


@patch("pytailor.clients.RestClient.new_workflow_definition",
       return_value=wf_def_model)
def test_add_to_account(mocked_method):
    wf_def = WorkflowDefinition(
        name='asdf',
        description='asdf',
        dag=DAG.from_dict(dag_data)
    )
    wf_def.add_to_account(Account(Mock()))
    assert wf_def.id == wf_def_model.id
    mocked_method.assert_called_once()


# @patch("pytailor.api.dag.DAG.to_dict",
#        return_value=dag_data)
def test_from_workflow():
    mock_wf = Mock(spec=Workflow)
    mock_wf.dag.to_dict.return_value = dag_data
    mock_wf.inputs = {}
    wf_def = WorkflowDefinition.from_workflow(
        wf=mock_wf,
        wf_def_name='asdf',
        wf_def_description='asdf',
    )


