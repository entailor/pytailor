import unittest
from files_data import *
import os
import pprint
from pytailor.api.schema import FilesSchema

class TestFiles(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_add_file_from_tag_ext(self):
        filesschema = FilesSchema()
        filesschema.add_file(files_ex1['tag'], files_ex1['ext'])
        pprint.pprint(filesschema.to_dict())

    def test_add_file(self):
        filesschema = FilesSchema()
        filesschema.add_file(**files_ex2)
        # pprint.pprint(filesschema.to_dict())

    def test_from_class(self):
        filesschema = FilesSchema(**files_ex3)
        pprint.pprint(filesschema.to_dict())

    def test_tojson(self):
        filesschema = FilesSchema(**files_ex3)
        filesschema.to_json('test.json')
        os.remove('test.json')


if __name__ == "__main__":
    suite1 = unittest.defaultTestLoader.loadTestsFromTestCase(TestFiles)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner().run(suite)
