from __future__ import annotations

from typing import Optional


class Parameterization:
    def __init__(self, name: str, parent: Optional[Parameterization] = None):
        self._name = name
        self._parent = parent
        self._items = {}

    def __getattr__(self, name):
        if not name.startswith("__"):
            setattr(self, name, Parameterization(name, self))
        return getattr(self, name)

    def __getitem__(self, item):
        if item in self._items:
            return self._items[item]
        else:
            parametrization = Parameterization(self._name + f"[{item}]", self._parent)
            self._items[item] = parametrization
            return parametrization

    def get_query(self):
        query = self._name
        parent = self._parent
        while parent:
            query = parent._name + "." + query
            parent = parent._parent
        return f"<% $.{query} %>"

    def __deepcopy__(self, memo):
        return self


class Inputs(Parameterization):
    def __init__(self):
        super().__init__(name="inputs")


class Outputs(Parameterization):
    def __init__(self):
        super().__init__(name="outputs")


class Files(Parameterization):
    def __init__(self):
        super().__init__(name="files")
