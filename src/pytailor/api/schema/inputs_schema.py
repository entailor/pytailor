"""
"""


from .strategies.tailorschemabuilder import TailorSchemaBuilder

# from jsonschema import validate # removed validation to not include dependency on jsonschema
import json


input_base_schema = {
    "title": "Inputs",
    "description": "Inputs for the Workflow",
    "outputs": {},
    "type": "object",
    "inputs": None,
}


class InputsSchema:
    """
    Generator for inputsschema to define workflow definition

    **Basic usage**

    Following example define a jsonschema, that sets "print" as a required property
    for inputs and that the value must be a string
    ``` python
    example_inputs = {'print': 'Hello, world!'}
    inputsschema = InputsSchema(inputs=example_inputs)
    ```
    Add 'Hello, world' as a default for property 'print'
    ``` python
    example_inputs = {'print': 'Hello, world!'}
    inputsschema.add_defaults(example_inputs) #
    ```

    Set 'Hello, world' and 'Hello, tailor!' as only allowed alternatives for property
    'print':

    ``` python
    enum_inputs = {'print': ['Hello, world!', 'Hello, tailor!']}
    inputsschema.add_enums(enum_inputs)
    ```




    **Parameters**

    - **inputs** (dict)
        Specify an example input schema that is valid for your workflow definition.

    """


    def __init__(self, inputs: dict):
        self.inputschema = self._build_jsonschema(inputs.copy())
        self.enum_inputs = None

    def add_defaults(self, default_inputs: dict):
        """
        ** Parameters **

        - ** default_inputs ** (dict) S
            Specify  an example
            input schema that is valid for your workflow definition with defaults.
        """

        self.default_inputs = default_inputs
        self._add_defaults()

    def add_enums(self, enum_inputs: dict):
        """
        ** Parameters **

        - ** enum_inputs ** (dict) S
            Specify altenatives for your inputsschema with a
            input schema where the property's values in a list represents the alternatives
        """

        self.enum_inputs = enum_inputs
        self._add_enums()

    @property
    def default_inputs(self):
        return self._default_inputs

    @default_inputs.setter
    def default_inputs(self, default_inputs):
        # validate(default_inputs, self.inputschema)
        self._default_inputs = default_inputs

    def to_dict(self):
        """Serialize input schema"""


        # self._rm_multiple_types()
        self._rm_multiple_types(self._inputschema)
        self._add_defeault_for_bool_none(self._inputschema)
        input_base_schema["inputs"] = self._inputschema
        return input_base_schema

    def to_json(self, filename, indent=4):
        """a json file"""
        json.dump(self.to_dict(), open(filename, "w+"), indent=indent)

    @property
    def inputschema(self):
        return self._inputschema

    @inputschema.setter
    def inputschema(self, jsonschema: dict):
        builder = TailorSchemaBuilder()
        builder.add_schema(jsonschema)
        self._inputschema = builder.to_schema()

    @staticmethod
    def _build_jsonschema(input_dict):
        builder = TailorSchemaBuilder()

        builder.add_schema({})
        assert isinstance(input_dict, dict), "inputs must be a dict"
        input_json = json.dumps(input_dict)
        input_dict = json.loads(input_json)
        builder.add_object(input_dict)
        return builder.to_schema()

    @staticmethod
    def _get_default(keys, default_inputs):
        for key in keys:
            if key in default_inputs.keys():
                default_inputs = default_inputs[key]
            else:
                return False
        return default_inputs

    def _add_defaults(self, item=None, key=None, keys=None):
        if keys is None:
            item = self.inputschema
            keys = []
        else:
            keys.append(key)
        if item["type"] == "object" and "properties" in item.keys():
            for key, val in item["properties"].items():
                self._add_defaults(val, key, keys.copy())
        elif item["type"] == "object":
            default = self._get_default(keys, self.default_inputs)
            if default:
                item["default"] = default
        elif item["type"] == "array":
            default = self._get_default(keys, self.default_inputs)
            if default:
                item["default"] = default
        elif item["type"] in ["number", "integer", "boolean", "string", "null"]:
            default = self._get_default(keys, self.default_inputs)
            if default:
                item["default"] = default

    @staticmethod
    def _get_enum(keys, enum_inputs):
        for key in keys:
            if key in enum_inputs.keys():
                enum_inputs = enum_inputs[key]
            else:
                return False
        assert isinstance(
            enum_inputs, list
        ), "to add enums the input values must be list"
        return enum_inputs

    def _add_enums(self, item=None, key=None, keys=None):
        if keys is None:
            item = self.inputschema
            keys = []
        else:
            keys.append(key)
        if item["type"] == "object" and "properties" in item.keys():
            for key, val in item["properties"].items():
                self._add_enums(val, key, keys.copy())
        elif item["type"] == "array":
            enum = self._get_enum(keys, self.enum_inputs)
            if enum:
                item["enum"] = enum
        elif item["type"] in ["number", "integer", "boolean", "string", "null"]:
            enum = self._get_enum(keys, self.enum_inputs)
            if enum:
                item["enum"] = enum

    def _rm_multiple_types(self, schema_dict, key="type"):
        if isinstance(schema_dict, list):
            for item in schema_dict:
                self._rm_multiple_types(item, key=key)
        if isinstance(schema_dict, dict):
            if schema_dict.get(key):
                if isinstance(schema_dict[key], list):
                    any_of = []
                    for listtype in schema_dict[key]:
                        any_of.append({"type": listtype, "title": listtype})
                    schema_dict.pop("type")
                    schema_dict.update({"anyOf": any_of})
            for this_key, value in schema_dict.items():
                self._rm_multiple_types(value, key=key)

    def _add_defeault_for_bool_none(self, schema_dict, key="type"):
        if isinstance(schema_dict, list):
            for item in schema_dict:
                self._add_defeault_for_bool_none(item, key=key)
        if isinstance(schema_dict, dict):
            if schema_dict.get(key):
                if schema_dict[key] == "boolean":
                    schema_dict.update({"default": False})
                elif schema_dict[key] == "null":
                    schema_dict.update({"default": None})

            for this_key, value in schema_dict.items():
                self._add_defeault_for_bool_none(value, key=key)
