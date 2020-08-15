import copy
from abc import ABC, abstractmethod
from typing import Optional, List, Union, Any
from enum import Enum


class TaskType(Enum):
    PYTHON = 'python'
    DUPLICATE = 'duplicate'
    DAG = 'dag'


def _flatten(container):
    """Iterate an arbitrary nested list/tuple
    """
    for i in container:
        if isinstance(i, (list, tuple)):
            for j in _flatten(i):
                yield j
        else:
            yield i


def _object_to_dict(obj, exclude_varnames=None):
    """Helper to serialize objects to dicts
    """
    exclude_varnames = exclude_varnames or []
    d = {}

    # get all potential variables
    objvars = vars(obj)
    for attr in dir(obj):
        if isinstance(getattr(type(obj), attr, None), property):
            objvars[attr] = getattr(obj, attr)

    for name, val in objvars.items():
        if name.startswith('_'):  # do not include private variables
            continue
        elif not bool(val):  # do not include empty variables
            continue
        elif name in exclude_varnames:  # name in exclude list
            continue
        # check if val has 'to_dict' method
        if callable(getattr(val, 'to_dict', None)):
            d[name] = val.to_dict()
        else:
            d[name] = val
    return d


def _object_from_dict(d):
    """Helper to deserialize objects from dicts
    """
    objtype = TaskType(d.pop('type'))
    if objtype == TaskType.PYTHON:
        return PythonTask.from_dict(d)
    elif objtype == TaskType.DUPLICATE:
        return DuplicateTask.from_dict(d)
    elif objtype == TaskType.DAG:
        return DAGTask.from_dict(d)


class BaseTask(ABC):
    """
    Base class for tasks.
    """

    def __init__(self, name: str = None, parents: any = None):
        parents = [parents] if isinstance(parents, (BaseTask, int)) else parents
        self.parents: list = parents if parents else []
        self.name: str = name or 'Unnamed'

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
    def from_dict(cls, d: dict) -> 'BaseTask':
        return NotImplemented


class PythonTask(BaseTask):
    """
    Task for running python code.

    Parameters
    ----------
    action : str
        Python callable. Must be importable in the executing python env. E.g.
        'mymodule.myfunc'.
    name : str, optional
        A default name is used if not provided.
    parents : BaseTask or List[BaseTask], optional
        Specify one or more upstream tasks that this task depends on.
    download : str or list, optional
        Provide one or more file tags. These file tags refer to files in
        the storage object associated with the workflow run.
    upload : dict, optional
        Specify files to send back to the storage object after a task has
        been run. Dict format is {tag1: val1, tag2: val2, ...} where val
        can be:
            1.  one or more query expressions(str og list) which is
                applied to the return value from *action*. File names resulting
                from the query are then uploaded to storage under the given
                tag.
            2.  one or more glob-style strings (str og list) which is
                applied in the task working dir. matching files are uploaded
                under the given tag.
    args : list or Any, optional
        Arguments to be passed as positional arguments to *action*. Arguments
        can be given as ordinary python values or as query expressions. See
        the examples for how query expressions are used.
    kwargs : dict or str, optional
        Arguments to be passed as keyword arguments to *action*. Arguments
        can be given as ordinary python values or as query expressions. See
        the examples for how query expressions are used.
    output_to : str, optional
        The return value of the action is stored in a tag with the specified name.
        This value is made available for later use through the expression $.outputs.<tag>.
    output_extraction : dict, optional
        An expression to extract parts of the return value of the action. The keys of the
        dictionary are used as tags, and the values becomes available for later use
        through the expressions $.outputs.<tag1>, $.outputs.<tag2>, and so on.
    """

    TYPE = TaskType.PYTHON

    def __init__(self,
                 action: str,
                 name: Optional[str] = None,
                 parents: Optional[Union[List[BaseTask], BaseTask]] = None,
                 download: Optional[Union[list, str]] = None,
                 upload: Optional[dict] = None,
                 args: Optional[Union[list, Any]] = None,
                 kwargs: Optional[Union[dict, str]] = None,
                 output_to: Optional[str] = None,
                 output_extraction: Optional[dict] = None
                 ):
        super().__init__(name=name, parents=parents)
        self.action = action
        self.kwargs = kwargs or {}
        self.args = args or []
        self.download = download or []
        self.upload = upload or {}
        self.output_to = output_to
        self.output_extraction = output_extraction

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value

    def to_dict(self):
        d = _object_to_dict(self, exclude_varnames=['parents'])
        d['type'] = self.TYPE.value
        return d

    @classmethod
    def from_dict(cls, d):
        d = copy.deepcopy(d)
        d.pop('type', None)
        return cls(**d)

    def copy(self):
        """
        Get a copy of this task definition without parent refs
        """
        return PythonTask.from_dict(self.to_dict())


class DuplicateTask(BaseTask):
    """
    Dynamically duplicate a task during a workflow run.

    Provides parallelization or "fan-out" functionality. The *task* object
    is duplicated based on the data provided with *args*, *kwargs*
    and *download*. At least one of these must be specified. Different
    formats of these arguments are allowed. See the examples/*duplicate*.py
    example scripts for different variations.

    Parameters
    ----------
    task : BaseTask
        Task to be duplicated (PythonTask, DuplicateTask or DAGTask).
    name : str, optional
        A default name is used if not provided.
    parents : BaseTask or List[BaseTask], optional
        Specify one or more upstream task definitions that this task definition
        depends on.
    download : str or list, optional
        Specify one or more file tags to be used as basis for duplication.
    args : str or list, optional
        Specify data to be used for *args* input in duplicated tasks Can be a single
        query expression or .
    kwargs : str or dict, optional
        Specify data to be used for *kwargs* input in duplicated task definitions

    """

    TYPE = TaskType.DUPLICATE

    def __init__(self,
                 task: BaseTask, name: str = None,
                 parents: Union[List[BaseTask], BaseTask] = None,
                 download: Union[list, str] = None,
                 args: Union[list, str] = None,
                 kwargs: Union[dict, str] = None
                 ):
        super().__init__(name=name, parents=parents)
        self.task = task
        self.download = download or []
        self.args = args
        self.kwargs = kwargs

    def to_dict(self):
        d = _object_to_dict(self, exclude_varnames=['parents'])
        d['type'] = self.TYPE.value
        return d

    @classmethod
    def from_dict(cls, d):
        d = copy.deepcopy(d)
        td = d.pop('task')
        d['task'] = _object_from_dict(td)
        d.pop('type', None)
        return cls(**d)

    def copy(self):
        """
        Get a copy of this definition without parent refs
        """
        return DuplicateTask.from_dict(self.to_dict())


class DAGTask(BaseTask):
    """
    Represents a Directed Acyclic Graph, i.e. a DAG.

    Parameters
    ----------
    tasks : BaseTask or List[BaseTask]
        Python, Duplicate or Workflow objects.
    name : str, optional
        A default name is used if not provided.
    parents : BaseTask or List[BaseTask], optional
        Specify one or more upstream task definitions that this task definition
        depends on.
    links : dict, optional
        Parent/children relationships can be specified with the dict on the form
        {parent_def: [child_def1, child_def2], ...}. Definition references may either
        be indices (ints) into *tasks* or BaseTask instances. Note that links
        may also be defined on task  objects with the *parents* argument instead of
        using links: (parents=[parent_def1, parent_def2])
    """

    TYPE = TaskType.DAG

    def __init__(self,
                 tasks: Union[List[BaseTask], BaseTask],
                 name: Optional[str] = None,
                 parents: Union[List[BaseTask], BaseTask] = None,
                 links: dict = None):

        super().__init__(name=name, parents=parents)
        self.tasks = tasks if isinstance(tasks, (list, tuple)) \
            else [tasks]

        links = links or {}
        links = self._as_index_links(links)
        task_links = self._as_task_links(links)

        # add empty list to task definitions without children
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
        self.task_def_links = task_links

        # Update parents in task definition objects
        for td in self.tasks:
            td.parents = self.__get_parents(td)

    def __get_parents(self, task):
        parents = set()  # fill with task definitions
        for p, cs in self.task_def_links.items():
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
        task_def_links = {}
        for p, cs in links.items():
            pi = self._as_task_def(p)
            cis = [self._as_task_def(c) for c in cs]
            task_def_links[pi] = cis
        return task_def_links

    def to_dict(self):
        d = _object_to_dict(self, exclude_varnames=[
            'tasks', 'task_links', 'parents'])
        d['tasks'] = [task.to_dict() for task in self.tasks]
        d['type'] = self.TYPE.value
        if not any(self.links.values()):  # no links exist, explicitly write empty dict
            d['links'] = {}
        return d

    @classmethod
    def from_dict(cls, d):
        d = copy.deepcopy(d)
        task_def_dicts = d.pop('tasks')
        task_defs = []
        for td in task_def_dicts:
            task_defs.append(_object_from_dict(td))
        link_dict = d.pop('links', None)
        if link_dict is not None:
            d['links'] = {int(k): v for k, v in link_dict.items()}
        d.pop('type', None)
        return cls(task_defs, **d)
