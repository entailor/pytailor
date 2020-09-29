import unittest
from input_data import *
from pytailor import InputsSchema
import genson
import os
import pprint
import jsonschema
schema_validator = jsonschema.Draft7Validator.check_schema


def genson_to_schema(inputs):
    builder = genson.SchemaBuilder()
    builder.add_schema()
    return builder.to_schema()


class TestInputs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.inputs1 = inputs1
        cls.inputs2 = inputs2
        cls.jsonschema1 = json_schema1

    @classmethod
    def tearDownClass(cls):
        pass

    def test_schema_from_inputs(self):
        inputs = InputsSchema(inputs1)
        self.assertFalse(schema_validator(inputs.inputschema))
        inputs = InputsSchema(inputs2)
        self.assertFalse(schema_validator(inputs.inputschema))

    def test_schema_from_schema(self):
        inputs = InputsSchema({})
        inputs.inputschema = json_schema2
        self.assertFalse(schema_validator(inputs.inputschema))

    def test_add_defaults(self):
        inputs = InputsSchema(inputs2)
        inputs.add_defaults(inputs2)
        pprint.pprint(inputs.inputschema)
        self.assertFalse(schema_validator(inputs.inputschema))

        inputs = InputsSchema({})
        inputs.inputschema = json_schema2
        inputs.add_defaults(json_schema2_defaults)
        self.assertFalse(schema_validator(inputs.inputschema))

        inputs = InputsSchema({})
        inputs.inputschema = json_schema3
        inputs.add_defaults(json_schema3_defaults)
        # pprint.pprint(inputs.inputschema)
        self.assertFalse(schema_validator(inputs.inputschema))



    def test_invalid_defaults(self):
        inputs = InputsSchema({})
        inputs.inputschema = json_schema2
        self.assertRaises(jsonschema.exceptions.ValidationError, inputs.add_defaults, json_schema2_invaliddefaults)

    def test_add_enums(self):
        inputs = InputsSchema({})
        inputs.inputschema = json_schema2
        inputs.add_enums(json_schema2_enums1)
        self.assertFalse(schema_validator(inputs.inputschema))
        # pprint.pprint(inputs.inputschema)

    def test_enum_not_as_list(self):
        inputs = InputsSchema({})
        inputs.inputschema = json_schema2
        self.assertRaises(AssertionError, inputs.add_enums, json_schema2_enumsnotvalid)

    def test_to_dict(self):
        inputs = InputsSchema({})
        inputs.inputschema = json_schema2
        self.assertEqual(inputs.inputschema, inputs.to_dict()['inputs'])

    def test_to_json(self):
        inputs = InputsSchema({})
        inputs.inputschema = json_schema2
        inputs.to_json('test.json')
        os.remove('test.json')

    def test_multiple_data(self):
        inputs = InputsSchema(inputs_multiple_datatypes)
        # pprint.pprint(inputs.to_dict())
        self.assertFalse(schema_validator(inputs.inputschema))

        inputs = InputsSchema(inputs_multiple_datatypes2)
        # pprint.pprint(inputs.to_dict())
        self.assertFalse(schema_validator(inputs.inputschema))

        inputs = InputsSchema(inputs_nested_anyof)
        # pprint.pprint(inputs.to_dict())
        self.assertFalse(schema_validator(inputs.inputschema))

        inputs = InputsSchema(inputs_nested_anyof2)
        # pprint.pprint(inputs.to_dict())
        self.assertFalse(schema_validator(inputs.inputschema))


    def test_bool(self):
        inputs = InputsSchema(inputs_bool)
        pprint.pprint(inputs.to_dict())
        inputs.add_defaults(inputs_bool)
        pprint.pprint(inputs.to_dict())


if __name__ == "__main__":
    suite1 = unittest.defaultTestLoader.loadTestsFromTestCase(TestInputs)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner().run(suite)
