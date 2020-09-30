from tests.api.schema.testdata.description_data import *
from pytailor import Description
import os
import pytest


def test_description_init_():
    description = Description("title", "description")
    assert description.to_string() == "description"
    assert description.name == "title"
    with pytest.raises(AssertionError):
        Description(2)


def test_description_from_dag():
    description = Description.from_dag(
        dag, wf_def_name=wf_def_name, wf_def_description=wf_def_description
    )
    assert description.name == wf_def_name
    assert description.string == description.to_string()
    description.to_markdown("test.MD")
    os.remove("test.MD")
