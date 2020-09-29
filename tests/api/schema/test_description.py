from description_data import *
import unittest
from pytailor import Description
import os
import pprint


class TestInputs(unittest.TestCase):

    def test_description_init_(self):
        description = Description('title', 'description')
        self.assertEqual(description.to_string(), 'description')
        self.assertEqual(description.name, 'title')
        self.assertRaises(AssertionError, Description, 2)

    def test_description_from_dag(self):
        description = Description.from_dag(dag,
                                           wf_def_name=wf_def_name,
                                           wf_def_description=wf_def_description)
        self.assertEqual(description.name, wf_def_name)
        self.assertEqual(description.string, description.to_string())
        description.to_markdown('test.MD')
        # pprint.pprint(description.to_string())


if __name__ == "__main__":
    suite1 = unittest.defaultTestLoader.loadTestsFromTestCase(TestInputs)
    suite = unittest.TestSuite([suite1])
    unittest.TextTestRunner().run(suite)
