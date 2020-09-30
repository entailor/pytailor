from genson.schema.strategies import Object


class AdditionalProperties(Object):
    # add 'minimum' to list of keywords
    KEYWORDS = (*Object.KEYWORDS, "additionalProperties")

    # create a new instance variable
    def __init__(self, node_class):
        super().__init__(node_class)
        self.additionalProperties = None

    # capture additionalProperties from schemas
    def add_schema(self, schema):
        super().add_schema(schema)
        if "additionalProperties" in schema:
            self.additionalProperties = schema["additionalProperties"]
        else:
            self.additionalProperties = True

    # set additionalProperties
    def add_object(self, obj):
        super().add_object(obj)
        self.additionalProperties = (
            True if self.additionalProperties is None else self.additionalProperties
        )

    # include 'additionalProperties' in the output
    def to_schema(self):
        schema = super().to_schema()
        schema["additionalProperties"] = self.additionalProperties
        # schema['additionalProperties'] = True
        return schema
