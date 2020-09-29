from typing import Union, List, Dict
import json

# todo: titles and descriptions should be asserted for type

files_base = {"in": {}}

class FilesSchema:

    def __init__(self, tags: List[str] = None, exts: List[List[str]] = None,
                 multiples: List[bool] = None, requireds: List[bool] = None,
                 titles: List[str] = None, descriptions: List[str] = None):

        self.tags = tags or []
        self.exts = exts or ['*']*len(self.tags)
        self.multiples = multiples or [False]*len(self.tags)
        self.requireds = requireds or [True]*len(self.tags)
        self.titles = titles or self.tags.copy()
        self.descriptions = descriptions or ['']*len(self.tags)

    def add_file(self, tag: str, ext: List[str] = ['*'],
                 multiple: bool = False, required: bool = True,
                 title: str = None, description: str = ''):
        if not title:
            title = tag

        if not description:
            description = ['']
        self._tags.append(tag)
        self._exts.append(ext)
        self._multiples.append(multiple)
        self._requireds.append(required)
        self.titles.append(title)
        self.descriptions.append(description)

    def to_dict(self):
        files_dict = files_base.copy()
        if not self.titles:
            self.titles = self.tags
        if not self.descriptions:
            self.descriptions = ['']*len(self.tags)
        for i in range(len(self.tags)):
            files_dict['in'].update({self.tags[i]: {
                'ext': self.exts[i],
                'title': self.titles[i],
                'description': self.descriptions[i],
                'multiple': self.multiples[i],
                'required': self.requireds[i],
            }})
        return files_dict

    def to_json(self, filename: str, indent: int = 4):
        files_dict = self.to_dict()
        json.dump(files_dict, open(filename, 'w+'), indent=indent)

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
                assert not e.startswith('.'), 'do not include . in extension name'
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
