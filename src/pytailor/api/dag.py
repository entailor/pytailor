from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import Optional, List, Union, Any, Dict, Callable
from enum import Enum

from pytailor.utils import as_query, walk_and_apply
from pytailor.exceptions import DAGError
from .parameterization import Parameterization

# Not thread safe, but this is considered ok
_CONTEXT_MANAGER_OWNER = None


class TaskType(Enum):
    PYTHON = "python"
    BRANCH = "branch"
    DAG = "dag"


def _object_to_dict(obj, exclude_varnames=None, allow_none_or_false=None):
    """Helper to serialize objects to dicts"""
    exclude_varnames = exclude_varnames or []
    allow_none_or_false = allow_none_or_false or []
    d = {}

    # get all potential variables
    objvars = vars(obj)
    for attr in dir(obj):
        if isinstance(getattr(type(obj), attr, None), property):
            objvars[attr] = getattr(obj, attr)

    for name, val in objvars.items():
        if name.startswith("_"):  # do not include private variables
            continue
        elif not bool(val) and name not in allow_none_or_false:
            continue
        elif name in exclude_varnames:  # name in exclude list
            continue
        # check if val has 'to_dict' method
        if callable(getattr(val, "to_dict", None)):
            d[name] = val.to_dict()
        else:
            d[name] = val
    return d


def _object_from_dict(d):
    """Helper to deserialize objects from dicts"""
    objtype = TaskType(d.pop("type"))
    if objtype == TaskType.PYTHON:
        return PythonTask.from_dict(d)
    elif objtype == TaskType.BRANCH:
        return BranchTask.from_dict(d)
    elif objtype == TaskType.DAG:
        return DAG.from_dict(d)


def _resolve_queries(d: dict):
    def val_apply_file_tags(v):
        if isinstance(v, Parameterization):
            return v.get_name()
        elif isinstance(v, str):
            return v
        resolved_download = []
        for tag in v:
            if isinstance(tag, Parameterization):
                resolved_download.append(tag.get_name())
            else:
                resolved_download.append(tag)
        return resolved_download

    def val_apply_output_to(v):
        return v.get_name() if isinstance(v, Parameterization) else v

    def val_apply_dict_keys(v):
        return {
            k.get_name() if isinstance(k, Parameterization) else k: val
            for k, val in v.items()
        }

    d_tmp = walk_and_apply(
        d,
        key_cond=lambda k: k == "output_to",
        val_apply=val_apply_output_to,
        key_apply_on=None,
        val_apply_on="key_cond",
    )
    d_tmp = walk_and_apply(
        d_tmp,
        key_cond=lambda k: k in {"output_extraction", "upload"},
        val_apply=val_apply_dict_keys,
        key_apply_on=None,
        val_apply_on="key_cond",
    )
    d_tmp = walk_and_apply(
        d_tmp,
        key_cond=lambda k: k in {"download", "branch_files"},
        val_apply=val_apply_file_tags,
        key_apply_on=None,
        val_apply_on="key_cond",
    )
    return walk_and_apply(
        d_tmp,
        val_cond=lambda v: isinstance(v, Parameterization),
        val_apply=lambda v: v.get_query(),
    )


def _resolve_callables(d: dict):
    def val_apply_function(v):
        if callable(v):
            return v.__module__ + "." + v.__name__
        else:
            return v

    return walk_and_apply(
        d,
        key_cond=lambda k: k == "function",
        val_apply=val_apply_function,
        key_apply_on=None,
        val_apply_on="key_cond",
    )


class BaseTask(ABC):
    """
    Base class for tasks.
    """

    def __init__(
        self,
        name: str = None,
        parents: Optional[Union[List[BaseTask], BaseTask]] = None,
        owner: Optional[OwnerTask] = None,
        requirements: Optional[List[str]] = None
    ):
        self.name: str = name or "Unnamed"
        parents = [parents] if isinstance(parents, (BaseTask, int)) else parents
        self.parents: list = parents if parents else []
        self.requirements = ['pytailor']
        self._update_requirements(requirements or [])
        if not owner and _CONTEXT_MANAGER_OWNER:
            owner = _CONTEXT_MANAGER_OWNER
        if owner:
            self.owner = owner
            self.owner.register(self)
            self._update_requirements(owner.requirements)

    @property
    @classmethod
    @abstractmethod
    def TYPE(cls) -> TaskType:
        return NotImplemented

    @abstractmethod
    def to_dict(self) -> dict:
        return NotImplemented

    @classmethod
    @abstractmethod
    def from_dict(cls, d: dict) -> BaseTask:
        return NotImplemented

    def _update_requirements(self, requirements):
        self.requirements = sorted(set(self.requirements).union(requirements))

    @abstractmethod
    def get_all_requirements(self) -> List[str]:
        return NotImplemented


class OwnerTask(BaseTask):
    """
    A task that own other tasks (DAG, BranchTask).
    """

    def __init__(
        self,
        name: Optional[str] = None,
        parents: Optional[Union[List[BaseTask], BaseTask]] = None,
        owner: Optional[BaseTask] = None,
        requirements: Optional[List[str]] = None
    ):
        super().__init__(name=name, parents=parents, owner=owner,
                         requirements=requirements)
        self._old_context_manager_owners = []

    @abstractmethod
    def register(self, task: BaseTask):
        return NotImplemented

    def __enter__(self):
        global _CONTEXT_MANAGER_OWNER
        self._old_context_manager_owners.append(_CONTEXT_MANAGER_OWNER)
        _CONTEXT_MANAGER_OWNER = self
        return self

    def __exit__(self, _type, _value, _tb):
        global _CONTEXT_MANAGER_OWNER
        _CONTEXT_MANAGER_OWNER = self._old_context_manager_owners.pop()


class PythonTask(BaseTask):
    """
    Task for running python code.

    **Basic usage**

    ``` python
    pytask = PythonTask(
        function='builtins.print',
        args='Hello, world!',
        name='My first task'
    )
    ```

    **Parameters**

    - **function** (str or Callable)
        Python callable. Must be importable in the executing python env.
    - **name** (str, optional)
        A default name is used if not provided.
    - **parents** (BaseTask or List[BaseTask], optional)
        Specify one or more upstream tasks that this task depends on.
    - **download** (str, list or Parameterization, optional)
        Provide one or more file tags. These file tags refer to files in
        the storage object associated with the workflow run.
    - **upload** (dict, optional)
        Specify files to send back to the storage object after a task has
        been run. Dict format is {tag1: val1, tag2: val2, ...} where val
        can be:

        -   one or more query expressions(str og list) which is
            applied to the return value from *callable*. File names resulting
            from the query are then uploaded to storage under the given
            tag.
        -   one or more glob-style strings (str og list) which is
            applied in the task working dir. matching files are uploaded
            under the given tag.

    - **args** (list, str or Parameterization, optional)
        Arguments to be passed as positional arguments to *function*. Accepts a list of
        ordinary python values, parameterization objects or query expressions. Also
        accepts a single single parameterization object or query expression which
        evaluate to a list. See the examples for how parameterization objects and query
        expressions are used.
    - **kwargs** (dict, str or Parameterization, optional)
        Arguments to be passed as keyword arguments to *function*. accepts a kwargs dict
        where values can be ordinary python values, parameterization objects or query
        expressions. Also accepts a single single parameterization object or query
        expression which evaluate to a dict. See the examples for how parameterization
        objects and query expressions are used.
    - **output_to** (str or Parameterization, optional)
        The return value of the callable is stored under the provided name in the
        workflow *outputs*. This value is then available for downstream task.
    - output_extraction (dict, optional)
        Provide a dict of *name: expr* where *expr* are query-expressions to extract
        parts of the return value of the callable. The keys of the dict are used as
        names for storing in the workflow *outputs* which becomes available for
        downstream tasks.
    - use_storage_dirs: (boolean, Optional)
        If True (default) files downloaded from storage are stored in a folder
        structure mirroring the storage
        If False files downloaded from storage are stored "flat" in the current directory
    - requirements: (list, optional)
        A list of requirements this task places on the worker environment
    """

    TYPE = TaskType.PYTHON

    def __init__(
        self,
        function: Union[str, Callable],
        name: Optional[str] = None,
        parents: Optional[Union[List[BaseTask], BaseTask]] = None,
        owner: Optional[BaseTask] = None,
        download: Optional[Union[List[str], str, Parameterization]] = None,
        upload: Optional[dict] = None,
        args: Optional[Union[list, str, Parameterization]] = None,
        kwargs: Optional[Union[Dict[str, Any], str, Parameterization]] = None,
        output_to: Optional[Union[str, Parameterization]] = None,
        output_extraction: Optional[dict] = None,
        use_storage_dirs: Optional[bool] = True,
        requirements: Optional[List[str]] = None
    ):
        super().__init__(name=name, parents=parents, owner=owner,
                         requirements=requirements)
        self.function = function
        self.kwargs = kwargs or {}
        self.args = args or []
        self.download = download or []
        self.upload = upload or {}
        self.output_to = output_to
        self.output_extraction = output_extraction
        self.use_storage_dirs = use_storage_dirs

        # check arguments here to avoid downstream errors
        if not (isinstance(self.args, (list, Parameterization)) or as_query(self.args)):
            raise TypeError(
                "*args* must be list, a parameterization object or query-expression.")
        if not (isinstance(self.kwargs, (dict, Parameterization)) or
                as_query(self.kwargs)):
            raise TypeError(
                "*args* must be list, a parameterization object or query-expression.")

    @property
    def function(self):
        return self._function

    @function.setter
    def function(self, value):
        self._function = value

    def to_dict(self) -> dict:
        """Serialize task definition."""
        d = _object_to_dict(self, exclude_varnames=["parents", "owner"],
                            allow_none_or_false=["use_storage_dirs"])
        d["type"] = self.TYPE.value
        return d

    @classmethod
    def from_dict(cls, d) -> PythonTask:
        """Create from serialized task definition."""
        d = copy.deepcopy(d)
        d.pop("type", None)
        return cls(**d)

    def copy(self):
        """
        Get a copy of this task definition without parent refs
        """
        return PythonTask.from_dict(self.to_dict())

    def get_all_requirements(self) -> List[str]:
        return self.requirements


class BranchTask(OwnerTask):
    """
    Dynamically *branch* a task or DAG during workflow execution.

    BranchTask Provides parallelization or "fan-out" functionality. The *task*
    is duplicated based on *branch_data* or *branch_files*. At least one of these must be
    specified.

    Parameters
    ----------
    task : BaseTask
        Task to be duplicated (PythonTask, BranchTask or DAG).
    name : str, optional
        A default name is used if not provided.
    parents : BaseTask or List[BaseTask], optional
        Specify one or more upstream tasks that this task
        depends on.
    branch_data : list or str, optional
        Data to be used as basis for branching. Accepts a query-expression or a list of
        query-expressions. The queries must evaluate to a list or a dict. If the query
        evaluates to a dict, that dict must have integer keys to represent the index of
        each branch.
    branch_files : list or str, optional
        Files to be used as basis for branching. Accepts a file tag or a list of
        file tags.
    requirements: (list, optional)
        A list of requirements this task places on the worker environment
    """

    TYPE = TaskType.BRANCH

    def __init__(
        self,
        task: BaseTask = None,
        name: str = None,
        parents: Union[List[BaseTask], BaseTask] = None,
        owner: Optional[OwnerTask] = None,
        branch_data: Union[list, str, Parameterization] = None,
        branch_files: Union[list, str, Parameterization] = None,
        requirements: Optional[List[str]] = None
    ):
        super().__init__(name=name, parents=parents, owner=owner,
                         requirements=requirements)
        self.task = task
        if task:
            task.owner = self
            task._update_requirements(self.requirements)

        # either branch_data of branch_files must be not None
        if branch_data is None and branch_files is None:
            raise ValueError("Either *branch_data* or *branch_files* must be specified")
        if branch_data is not None:
            self.branch_data = (
                [branch_data] if isinstance(branch_data, (str, Parameterization))
                else branch_data
            )
        if branch_files is not None:
            self.branch_files = (
                [branch_files] if isinstance(branch_files, (str, Parameterization))
                else branch_files
            )

    def to_dict(self) -> dict:
        d = _object_to_dict(self, exclude_varnames=["parents", "owner"])
        d["type"] = self.TYPE.value
        return d

    @classmethod
    def from_dict(cls, d) -> BranchTask:
        d = copy.deepcopy(d)
        td = d.pop("task")
        d["task"] = _object_from_dict(td)
        d.pop("type", None)
        return cls(**d)

    def copy(self):
        """
        Get a copy of this definition without parent refs
        """
        return BranchTask.from_dict(self.to_dict())

    def register(self, task: BaseTask) -> None:
        if self.task:
            raise DAGError(
                "Cannot register task with BranchTask. " "A task is already registered."
            )
        self.task = task

    def get_all_requirements(self) -> List[str]:
        requirements = set(self.requirements)
        if self.task:
            requirements.update(self.task.get_all_requirements())
        return sorted(requirements)


class DAG(OwnerTask):
    """
    Represents a Directed Acyclic Graph, i.e. a DAG.

    Parameters
    ----------
    tasks : BaseTask or List[BaseTask]
        PythonTask, BranchTask or DAG objects.
    name : str, optional
        A default name is used if not provided.
    parents : BaseTask or List[BaseTask], optional
        Specify one or more upstream tasks that this task
        depends on.
    links : dict, optional
        Parent/children relationships can be specified with the dict on the form
        {parent_def: [child_def1, child_def2], ...}. Definition references may either
        be indices (ints) into *tasks* or BaseTask instances. Note that links
        may also be defined on task  objects with the *parents* argument instead of
        using links: (parents=[parent_def1, parent_def2])
    requirements: (list, optional)
        A list of requirements this task places on the worker environment
    """

    TYPE = TaskType.DAG

    def __init__(
        self,
        tasks: Union[List[BaseTask], BaseTask] = None,
        name: Optional[str] = None,
        parents: Union[List[BaseTask], BaseTask] = None,
        owner: Optional[OwnerTask] = None,
        links: dict = None,
        requirements: Optional[List[str]] = None
    ):
        super().__init__(name=name, parents=parents, owner=owner,
                         requirements=requirements)
        if tasks:
            self.tasks = tasks if isinstance(tasks, (list, tuple)) else [tasks]
            for task in tasks:
                task.owner = self
                task._update_requirements(self.requirements)
        else:
            self.tasks = []
        self.links = links or {}
        self.__refresh_links()

    def __refresh_links(self):
        links = self.links
        links = self._as_index_links(links)
        task_links = self._as_task_links(links)

        # add empty list to tasks without children
        for i, td in enumerate(self.tasks):
            if i not in links:
                links[i] = []
                task_links[td] = []

        # convert parent links
        for i, td in enumerate(self.tasks):
            parent_indices = [self._as_index(pt) for pt in td.parents]
            for pi in parent_indices:
                if i not in links[pi]:
                    links[pi].append(i)
            parent_task_defs = [self._as_task_def(pt) for pt in td.parents]
            for ptd in parent_task_defs:
                if td not in task_links[ptd]:
                    task_links[ptd].append(td)

        self.links = links
        self.task_links = task_links

        # Update parents in task objects
        for td in self.tasks:
            td.parents = self.__get_parents(td)

    def __get_parents(self, task):
        parents = set()  # fill with task definitions
        for p, cs in self.task_links.items():
            if task in cs:
                parents.add(p)

        def sort_by_index(x):
            return self.tasks.index(x)

        # sort parents in order to have a stable ordering between runs
        sorted_parents = sorted(list(parents), key=sort_by_index)
        return sorted_parents

    def _as_index(self, td):
        return td if isinstance(td, int) else self.tasks.index(td)

    def _as_task_def(self, td):
        return self.tasks[td] if isinstance(td, int) else td

    def _as_index_links(self, links):
        index_links = {}
        for p, cs in links.items():
            pi = self._as_index(p)
            cis = [self._as_index(c) for c in cs]
            index_links[pi] = cis
        return index_links

    def _as_task_links(self, links):
        task_links = {}
        for p, cs in links.items():
            pi = self._as_task_def(p)
            cis = [self._as_task_def(c) for c in cs]
            task_links[pi] = cis
        return task_links

    def to_dict(self):
        d = _object_to_dict(
            self, exclude_varnames=["tasks", "task_links", "parents", "owner"]
        )
        d["tasks"] = [task.to_dict() for task in self.tasks]
        d["type"] = self.TYPE.value
        if not any(self.links.values()):  # no links exist, explicitly write empty dict
            d["links"] = {}
        d = _resolve_queries(d)
        d = _resolve_callables(d)
        return d

    @classmethod
    def from_dict(cls, d) -> DAG:
        d = copy.deepcopy(d)
        task_def_dicts = d.pop("tasks")
        task_defs = []
        for td in task_def_dicts:
            task_defs.append(_object_from_dict(td))
        link_dict = d.pop("links", None)
        if link_dict is not None:
            d["links"] = {int(k): v for k, v in link_dict.items()}
        d.pop("type", None)
        return cls(task_defs, **d)

    def register(self, task: BaseTask) -> None:
        if task in self.tasks:
            raise DAGError(
                "Cannot register task with DAG." "Task is already registered."
            )
        self.tasks.append(task)
        self.__refresh_links()

    def get_all_requirements(self) -> List[str]:
        requirements = set(self.requirements)
        for task in self.tasks:
            requirements.update(task.get_all_requirements())
        return sorted(requirements)
