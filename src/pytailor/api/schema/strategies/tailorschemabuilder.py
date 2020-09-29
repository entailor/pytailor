from genson import SchemaBuilder
from .additionalProperties import AdditionalProperties

# from .disable_multiple_types import Diablemultipletypes

"""
new SchemaBuilder class that uses the given strategies in addition
 to the existing strategies. See genson for more info.
"""


class TailorSchemaBuilder(SchemaBuilder):
    """ all object nodes include additional properties """

    EXTRA_STRATEGIES = (AdditionalProperties,)
