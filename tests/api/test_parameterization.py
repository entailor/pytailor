import pytest

from pytailor import Inputs, Outputs, Files
from pytailor.api.parameterization import Parameterization
from pytailor.exceptions import ParameterizationError


def test_inputs():
    inputs = Inputs()

    inputs_parameters = [
        inputs.param1,
        inputs.data.value1,
        inputs.data.value2,
        inputs.list1[0],
        inputs.nested_list[0][1]
    ]

    # do lookup of existing parameters
    assert isinstance(inputs.param1, Parameterization)
    assert isinstance(inputs.data.value1, Parameterization)
    assert isinstance(inputs.data.value2, Parameterization)
    assert isinstance(inputs.list1[0], Parameterization)
    assert isinstance(inputs.ested_list[0][1], Parameterization)

    target_queries = [
        "<% $.inputs.param1 %>",
        "<% $.inputs.data.value1 %>",
        "<% $.inputs.data.value2 %>",
        "<% $.inputs.list1[0] %>",
        "<% $.inputs.nested_list[0][1] %>",
    ]

    target_names = [
        "param1",
        "value1",
        "value2",
        "list1[0]",
        "nested_list[0][1]",
    ]

    resolved_queries = [p.get_query() for p in inputs_parameters]
    resolved_names = [p.get_name() for p in inputs_parameters]

    assert resolved_queries == target_queries
    assert resolved_names == target_names


def test_inputs_raises():
    inputs = Inputs()

    with pytest.raises(TypeError) as e:
        inputs.data["key"]
        assert "Only integer indices allowed" in str(e)


def test_outputs():
    outputs = Outputs()

    outputs_parameters = [
        outputs.param1,
        outputs.data.value1,
        outputs.data.value2,
        outputs.list1[0],
        outputs.nested_list[0][1]
    ]

    target_queries = [
        "<% $.outputs.param1 %>",
        "<% $.outputs.data.value1 %>",
        "<% $.outputs.data.value2 %>",
        "<% $.outputs.list1[0] %>",
        "<% $.outputs.nested_list[0][1] %>",
    ]

    target_names = [
        "param1",
        "value1",
        "value2",
        "list1[0]",
        "nested_list[0][1]",
    ]

    resolved_queries = [p.get_query() for p in outputs_parameters]
    resolved_names = [p.get_name() for p in outputs_parameters]

    assert resolved_queries == target_queries
    assert resolved_names == target_names


def test_outputs_legal_name_refs():
    outputs = Outputs()
    outputs.legalname.check_is_legal_name_ref()


def test_outputs_raises():
    outputs = Outputs()
    with pytest.raises(ParameterizationError) as e:
        outputs.asdf[0].check_is_legal_name_ref()
        assert "Illegal parameter reference." == str(e)

    with pytest.raises(ParameterizationError) as e:
        outputs.asdf[0].check_is_legal_name_ref("arg_name")
        assert "arg_name" in str(e)

    with pytest.raises(ParameterizationError) as e:
        outputs.asdf.fdsa.check_is_legal_name_ref()

    with pytest.raises(TypeError) as e:
        outputs.data["key"]
        assert "Only integer indices allowed" in str(e)


def test_files():
    files = Files()
    
    files_parameters = [
        files.param1,
        files.data.value1,
        files.data.value2,
        files.list1[0],
        files.nested_list[0][1]
    ]

    target_queries = [
        "<% $.files.param1 %>",
        "<% $.files.data.value1 %>",
        "<% $.files.data.value2 %>",
        "<% $.files.list1[0] %>",
        "<% $.files.nested_list[0][1] %>",
    ]

    target_names = [
        "param1",
        "value1",
        "value2",
        "list1[0]",
        "nested_list[0][1]",
    ]

    resolved_queries = [p.get_query() for p in files_parameters]
    resolved_names = [p.get_name() for p in files_parameters]

    assert resolved_queries == target_queries
    assert resolved_names == target_names


def test_files_legal_name_refs():
    files = Files()
    files.legalname.check_is_legal_name_ref()


def test_files_raises():
    files = Files()
    with pytest.raises(ParameterizationError) as e:
        files.asdf[0].check_is_legal_name_ref()
        assert "Illegal parameter reference." == str(e)

    with pytest.raises(ParameterizationError) as e:
        files.asdf[0].check_is_legal_name_ref("arg_name")
        assert "arg_name" in str(e)

    with pytest.raises(ParameterizationError) as e:
        files.asdf.fdsa.check_is_legal_name_ref()

    with pytest.raises(TypeError) as e:
        files.data["key"]
        assert "Only integer indices allowed" in str(e)
