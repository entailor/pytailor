from tests.api.schema.testdata.files_data import *
from pytailor import FilesSchema
import os
import pprint


def test_add_file_from_tag_ext():
    filesschema = FilesSchema()
    filesschema.add_file(files_ex1['tag'], files_ex1['ext'])


def test_add_file():
    filesschema = FilesSchema()
    filesschema.add_file(**files_ex2)
    # pprint.pprint(filesschema.to_dict())


def test_from_class():
    filesschema = FilesSchema(**files_ex3)
    pprint.pprint(filesschema.to_dict())


def test_tojson():
    filesschema = FilesSchema(**files_ex3)
    filesschema.to_json('test.json')
    os.remove('test.json')

