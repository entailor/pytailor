from tests.api.schema.testdata.input_data import *
from pytailor import InputsSchema
import pprint
import pytest
import jsonschema
schema_validator = jsonschema.Draft7Validator.check_schema


def test_schema_from_inputs():
    inputs = InputsSchema(inputs1)
    assert not schema_validator(inputs.inputschema)
    inputs = InputsSchema(inputs2)
    assert not schema_validator(inputs.inputschema)


def test_schema_from_schema():
    inputs = InputsSchema({})
    inputs.inputschema = json_schema2
    assert not schema_validator(inputs.inputschema)


def test_add_defaults():
    inputs = InputsSchema(inputs2)
    inputs.add_defaults(inputs2)

    pprint.pprint(inputs.inputschema)
    assert not schema_validator(inputs.inputschema)

    inputs = InputsSchema({})
    inputs.inputschema = json_schema2
    inputs.add_defaults(json_schema2_defaults)
    assert not schema_validator(inputs.inputschema)


def test_invalid_defaults():
    inputs = InputsSchema({})
    inputs.inputschema = json_schema2
    with pytest.raises(jsonschema.exceptions.ValidationError):
        inputs.add_defaults(json_schema2_invaliddefaults)


def test_add_enums():
    inputs = InputsSchema({})
    inputs.inputschema = json_schema2
    inputs.add_enums(json_schema2_enums1)
    assert not schema_validator(inputs.inputschema)


def test_enum_not_as_list():
    inputs = InputsSchema({})
    inputs.inputschema = json_schema2
    with pytest.raises(AssertionError):
        inputs.add_enums(json_schema2_enumsnotvalid)


def test_to_dict():
    inputs = InputsSchema({})
    inputs.inputschema = json_schema2
    assert inputs.inputschema == inputs.to_dict()['inputs']

def test_multiple_data():
    inputs = InputsSchema(inputs_multiple_datatypes)
    # pprint.pprint(inputs.to_dict())
    assert not schema_validator(inputs.inputschema)

    inputs = InputsSchema(inputs_multiple_datatypes2)
    # pprint.pprint(inputs.to_dict())
    assert not schema_validator(inputs.inputschema)

    inputs = InputsSchema(inputs_nested_anyof)
    # pprint.pprint(inputs.to_dict())
    assert not schema_validator(inputs.inputschema)

    inputs = InputsSchema(inputs_nested_anyof2)
    # pprint.pprint(inputs.to_dict())
    assert not schema_validator(inputs.inputschema)


def test_bool():
    inputs = InputsSchema(inputs_bool)
    inputs.add_defaults(inputs_bool)


