import json
import os
from typing import List

# todo: titles and descriptions should be asserted for type
from ..dag import DAG
from ..fileset import FileSet

files_base = {"in": {}}


class FilesSchema:
    """
    Generator for filesschema to define workflow definition

    **Basic usage**

    ``` python

    files_ex1 = {
    "tag": "my_tag",
    "ext": ["txt"],
    }
    filesschema = FilesSchema()
    filesschema.add_file(tag="my_tag", ext=["txt"])

    files_ex2 = {
    "tag": "my__new_tag",
    "ext": ["txt"],
    "title": "Coordinates",
    "multiple": True,
    "description": "A file with coordinate values of nodes",
    "required": True,
    }
    filesschema = FilesSchema()
    filesschema.add_file(**files_ex2)

    ```

    **Parameters**

    - **inputs** (dict)
        Specify an example input schema that is valid for your workflow definition.

    """

    def __init__(
        self,
        tags: List[str] = None,
        exts: List[List[str]] = None,
        multiples: List[bool] = None,
        requireds: List[bool] = None,
        titles: List[str] = None,
        descriptions: List[str] = None,
    ):

        self.tags = tags or []
        self.exts = exts or ["*"] * len(self.tags)
        self.multiples = multiples or [False] * len(self.tags)
        self.requireds = requireds or [True] * len(self.tags)
        self.titles = titles or self.tags.copy()
        self.descriptions = descriptions or [""] * len(self.tags)

    def add_file(
        self,
        tag: str,
        ext: List[str] = None,
        multiple: bool = False,
        required: bool = True,
        title: str = None,
        description: str = "",
    ):
        """
        **Parameters**

        - **tag** (str)
            Specify tag for file.
        - **tag** (str)
            Specify allowed extension for file
        - **mutiple** (bool)
            Specify whether multiples files are allowed
        - **required** (bool)
            Specify whether  file(s) are required
        - **title** (str)
            Specify the title to be shown in GUI
        - **description** (str)
            Specify the description to be shown in GUI
        """

        if not title:
            title = tag

        if not description:
            description = [""]
        self._tags.append(tag)
        self._exts.append(ext or ["*"])
        self._multiples.append(multiple)
        self._requireds.append(required)
        self.titles.append(title)
        self.descriptions.append(description)

    def to_dict(self):
        """Serialize files schema"""
        files_dict = files_base.copy()
        if not self.titles:
            self.titles = self.tags
        if not self.descriptions:
            self.descriptions = [""] * len(self.tags)
        for i in range(len(self.tags)):
            files_dict["in"].update(
                {
                    self.tags[i]: {
                        "ext": self.exts[i],
                        "title": self.titles[i],
                        "description": self.descriptions[i],
                        "multiple": self.multiples[i],
                        "required": self.requireds[i],
                    }
                }
            )
        return files_dict

    def to_json(self, filename: str, indent: int = 4):
        files_dict = self.to_dict()
        json.dump(files_dict, open(filename, "w+"), indent=indent)

    @classmethod
    def from_fileset_and_dag(cls, fileset: FileSet, dag: DAG):
        download_tags = []
        cls._get_file_tags(dag.to_dict(), key="download", tags=download_tags)
        upload_tags = []
        cls._get_file_tags(dag.to_dict(), key="upload", tags=upload_tags)
        files_schema = cls()
        for tag in download_tags:
            if tag not in upload_tags:
                files = fileset.list_files(tags=[tag])[0]["filenames"]
                multiple = True if len(files) > 1 else False
                ext = list(set([os.path.splitext(file)[1] for file in files]))
                files_schema.add_file(tag=tag,
                                      ext=ext,
                                      required=True,
                                      multiple=multiple)
        return files_schema

    @classmethod
    def _get_file_tags(cls, dag_item, key="download", tags=None):
        if tags is None:
            tags = []
        if isinstance(dag_item, dict):
            if dag_item.get(key):
                tag = dag_item.get(key)
                if isinstance(tag, dict):
                    tag = list(tag.keys())
                if not isinstance(tag, list):
                    tag = [tag]
                tags.extend(tag)
            if dag_item.get("tasks"):
                cls._get_file_tags(dag_item["tasks"], key, tags)
            if dag_item.get("task"):
                cls._get_file_tags(dag_item["task"], key, tags)
        if isinstance(dag_item, list):
            for sub_item in dag_item:
                cls._get_file_tags(sub_item, key, tags)

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags):
        assert isinstance(tags, list)
        for tag in tags:
            assert isinstance(tag, str)
        self._tags = tags

    @property
    def exts(self):
        return self._exts

    @exts.setter
    def exts(self, exts):
        assert isinstance(exts, list)
        for ext in exts:
            assert isinstance(ext, list)
            for e in ext:
                assert not e.startswith("."), "do not include . in extension name"
            assert len(self.tags) == len(exts)
        self._exts = exts

    @property
    def multiples(self):
        return self._multiples

    @multiples.setter
    def multiples(self, multiples):
        assert isinstance(multiples, list)
        for multiple in multiples:
            assert isinstance(multiple, bool)
        assert len(self.tags) == len(multiples)
        self._multiples = multiples

    @property
    def requireds(self):
        return self._requireds

    @requireds.setter
    def requireds(self, requireds):
        assert isinstance(requireds, list)
        for required in requireds:
            assert isinstance(required, bool)
        assert len(self.tags) == len(requireds)
        self._requireds = requireds
