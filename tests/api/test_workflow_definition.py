from unittest.mock import patch, Mock
import pytest
from tests.api.schema.testdata.input_data import inputs1
from pytailor import WorkflowDefinition, DAG, Account, Workflow
from pytailor.models import WorkflowDefinition as WorkflowDefinitionModel

from .schema.test_inputs import schema_validator
from ..data import dag_data, data_workflow


@pytest.fixture(scope='session', autouse=True)
def dag():
    return DAG.from_dict(dag_data)


def test_create_wf_def():
    wf_def = WorkflowDefinition(
        name='asdf',
        description='asdf',
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
    assert wf_def.id == 'asdf'
    mocked_method.assert_called_once()


def test_from_workflow():
    mock_wf = Mock(spec=Workflow)
    mock_wf.dag = DAG.from_dict(dag_data)
    mock_wf.inputs = inputs1
    wf_def = WorkflowDefinition.from_workflow(
        wf=mock_wf,
        wf_def_name='asdf',
        wf_def_description='asdf',
    )
    wf_def_dagdict = wf_def.dag.to_dict()
    assert wf_def_dagdict['name'] == dag_data['name']
    assert not schema_validator(wf_def.inputs_schema)
