import copy
from abc import abstractmethod
from collections import defaultdict
from typing import Optional
from typing import Union

from tailor.serializable import Serializable


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
    objtype = d.pop('type')
    if objtype == 'python':
        return PythonTask.from_dict(d)
    elif objtype == 'duplicate':
        return DuplicateTask.from_dict(d)
    elif objtype == 'dag':
        return DAGTask.from_dict(d)


class TaskDefinition(Serializable):
    """
    Base class for definitions.
    """

    def __init__(self, name: str = None, parents: any = None):
        parents = [parents] if isinstance(parents, (TaskDefinition, int)) else parents
        self.parents: list = parents if parents else []
        self.name: str = name or 'Unnamed'

    @property
    @classmethod
    @abstractmethod
    def TYPE(cls) -> str:
        return NotImplemented

    def __repr__(self):
        r = f'{type(self).__name__}(name={self.name})'
        return r


class SingleTask(TaskDefinition):
    pass


class PythonTask(SingleTask):
    """
    Task definition for running python code.

    Parameters
    ----------
    action : str
        Python callable. Must be importable in the executing python env. E.g.
        'mymodule.myfunc'.
    name : str, optional
        TaskDefinition name. A default name is used if not provided.
    parents : TaskDefinition or list, optional
        Specify one or more upstream task definitions that this task definition depends on.
    download : str or list, optional
        Provide one or more file tags. These file tags refer to files in
        the storage object associated with the workflow run.
    download_filter : str or list, optional
        Download files by applying one or more filename filters (glob-style).
        NOT IMPLEMENTED
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
    args : list, optional
        Arguments to be passed as positional arguments to *action*. Arguments
        can be given as ordinary python values or as query expressions. See
        the examples for how query expressions are used.
    kwargs : dict, optional
        Arguments to be passed as keyword arguments to *action*. Arguments
        can be given as ordinary python values or as query expressions. See
        the examples for how query expressions are used.
    output_to : str, optional
        The return value of the action is stored in a tag with the specified name.
        This value is made available for later use through the expression $.outputs.<tag>.
    output_extraction : dict, optional
        An expression to extract parts of the return value of the action. The keys of the
        dictionary are used as tags,
        and the values becomes available for later use through the expressions
        $.outputs.<tag1>, $.outputs.<tag2>, and so on.
    """

    TYPE = 'python'

    def __init__(self,
                 action: str,
                 name: Optional[str] = None,
                 parents: Optional[Union[list, TaskDefinition]] = None,
                 download: Optional[Union[list, str]] = None,
                 download_filter: Optional[Union[list, str]] = None,
                 upload: Optional[dict] = None,
                 args: Optional[Union[list, str]] = None,
                 kwargs: Optional[dict] = None,
                 output_to: Optional[str] = None,
                 output_extraction: Optional[dict] = None):
        super().__init__(name=name, parents=parents)
        self.action = action
        self.kwargs = kwargs or {}
        self.args = args or []
        self.download = download or []
        self.download_filter = [download_filter] if isinstance(download_filter, str) \
            else download_filter
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
        d['type'] = self.TYPE
        return d

    def to_db_dict(self):
        d = _object_to_dict(self, exclude_varnames=[])
        d['type'] = self.TYPE
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


class DuplicateTask(SingleTask):
    """
    Dynamically duplicate a TaskDefinition, e.g. a PythonTask, during workflow execution.

    Provides parallelization or "fan-out" functionality. The *task_def* object
    is duplicated based on the data provided with *args*, *kwargs*
    and *download*. At least one of these must be specified. Different
    formats of these arguments are allowed. See the examples/*duplicate*.py
    example scripts for different variations.

    Parameters
    ----------
    task_def : TaskDefinition
        TaskDefinition (PythonTask, DuplicateTask or DAGTask) to be duplicated.
    name : str, optional
        TaskDefinition name. A default name is used if not provided.
    parents : TaskDefinition or list, optional
        Specify one or more upstream task definitions that this task definition depends on.
    download : str or list, optional
        Specify one or more file tags to be used as basis for duplication.
    args : str or list, optional
        Specify data to be used for *args* input in duplicated task definitions.
    kwargs : str or dict, optional
        Specify data to be used for *kwargs* input in duplicated task definitions

    """

    TYPE = 'duplicate'

    def __init__(self, task_def: TaskDefinition, name: str = None, parents: Union[list, TaskDefinition] = None,
                 download: Union[list, str] = None, args: Union[list, str] = None, kwargs: Union[dict, str] = None):
        super().__init__(name=name, parents=parents)
        self.task_def = task_def
        self.download = download or []
        self.args = args
        self.kwargs = kwargs

    def to_dict(self):
        d = _object_to_dict(self, exclude_varnames=['parents'])
        d['type'] = self.TYPE
        return d

    def to_db_dict(self):
        d = _object_to_dict(self, exclude_varnames=[])
        d['type'] = self.TYPE
        return d

    @classmethod
    def from_dict(cls, d):
        d = copy.deepcopy(d)
        td = d.pop('task_def')
        d['task_def'] = _object_from_dict(td)
        d.pop('type', None)
        return cls(**d)

    def copy(self):
        """
        Get a copy of this definition without parent refs
        """
        return DuplicateTask.from_dict(self.to_dict())


class GroupTask(TaskDefinition):
    pass


class DAGTask(GroupTask):
    """
    Represents a Directed Acyclic Graph, i.e. a DAG.

    Parameters
    ----------
    task_defs : A single TaskDefinition or a list of TaskDefinitions
        Python, Duplicate or WorkflowModel objects.
    name : str, optional
        WorkflowModel name. A default name is used if not provided.
    parents : TaskDefinition or list, optional
        Specify one or more upstream task definitions that this task definition
        depends on.
    links : dict, optional
        Parent/children relationships can be specified with the dict on the form
        {parent_def: [child_def1, child_def2], ...}. Definition references may either
        be indices (ints) into *task_defs* or TaskDefinition instances. Note that links
        may also be defined on task definition objects with keyword argument
        parents=[parent_def1, parent_def2])
    """

    TYPE = 'dag'

    # IDEA: Option to run a workflow in a "shared python session" or something.
    #       This means that objects can be passed between tasks without
    #       serialization/deserialization. The context concept is used the same
    #       way, but objects are kept alive throughout execution of the tasks.
    #       local context mode?

    def __init__(self, task_defs: Union[TaskDefinition, list], name: str = None,
                 parents: Union[TaskDefinition, list] = None, links: dict = None):

        super().__init__(name=name, parents=parents)
        self.task_defs = task_defs if isinstance(task_defs, (list, tuple)) \
            else [task_defs]

        links = links or {}
        links = self._as_index_links(links)
        task_def_links = self._as_task_def_links(links)

        # add empty list to task definitions without children
        for i, td in enumerate(self.task_defs):
            if i not in links:
                links[i] = []
                task_def_links[td] = []

        # convert parent links
        for i, td in enumerate(self.task_defs):
            parent_indices = [self._as_index(pt) for pt in td.parents]
            for pi in parent_indices:
                if i not in links[pi]:
                    links[pi].append(i)
            parent_task_defs = [self._as_task_def(pt) for pt in td.parents]
            for ptd in parent_task_defs:
                if td not in task_def_links[ptd]:
                    task_def_links[ptd].append(td)

        self.links = links
        self.task_def_links = task_def_links

        # Update parents in task definition objects
        for td in self.task_defs:
            td.parents = self.__get_parents(td)

    def __get_parents(self, task_def):
        parents = set()  # fill with task definitions
        for p, cs in self.task_def_links.items():
            if task_def in cs:
                parents.add(p)

        def sort_by_index(x):
            return self.task_defs.index(x)

        # sort parents in order to have a stable ordering between runs
        sorted_parents = sorted(list(parents), key=sort_by_index)
        return sorted_parents

    def _as_index(self, td):
        return td if isinstance(td, int) else self.task_defs.index(td)

    def _as_task_def(self, td):
        return self.task_defs[td] if isinstance(td, int) else td

    def _as_index_links(self, links):
        index_links = {}
        for p, cs in links.items():
            pi = self._as_index(p)
            cis = [self._as_index(c) for c in cs]
            index_links[pi] = cis
        return index_links

    def _as_task_def_links(self, links):
        task_def_links = {}
        for p, cs in links.items():
            pi = self._as_task_def(p)
            cis = [self._as_task_def(c) for c in cs]
            task_def_links[pi] = cis
        return task_def_links

    def __remove_redundant_links(self, task_defs):
        # transitive reduction of DAG using DFS (depth first search)
        class Graph:
            def __init__(self):
                self.graph = defaultdict(list)

            def add_edge(self, u, v):
                self.graph[u].append(v)

            def DFSUtil(self, v, visited, vertices):
                visited[v] = True
                vertices.append(v)
                for node in self.graph[v]:
                    if not visited[node]:
                        self.DFSUtil(node, visited, vertices)

            def DFS(self, v):
                # visited = [False] * (len(self.graph))
                visited = defaultdict(lambda: False)
                vertices = []
                self.DFSUtil(v, visited, vertices)
                return vertices

        g = Graph()
        for i, d in enumerate(task_defs):
            for p in d.parents:
                g.add_edge(i, task_defs.index(p))

        for u in list(g.graph):
            for v in g.graph[u]:
                reachable = g.DFS(v)
                if len(reachable) > 1:
                    for v2 in reachable[1:]:
                        if task_defs[v2] in task_defs[u].parents:
                            task_defs[u].parents.remove(task_defs[v2])

    def __apply_links_to_task_defs(self, task_defs):
        """
        """
        for task, d in zip(task_defs, self.task_defs):
            # alt 1: SingleTaskModel
            # alt 2: GroupTask

            if isinstance(d, SingleTask):  # alt 1:
                parents = []
                for pd in d.parents:
                    index = self.task_defs.index(pd)
                    if isinstance(task_defs[index], list):  # parent is GroupTask
                        parents.extend(pd._resolved_tasks)
                    else:
                        # parent is SingleTaskModel
                        parents.append(task_defs[index])
                task.parents = parents

            else:  # alt 2:
                for taski in task:
                    parents = []
                    for pd in d.parents:
                        index = self.task_defs.index(pd)
                        if isinstance(pd, DAGTask):
                            parents.append(pd._resolved_tasks)
                        else:
                            parents.append(task_defs[index])
                    taski.parents.extend(parents)

    def to_dict(self):
        d = _object_to_dict(self, exclude_varnames=[
            'task_defs', 'task_def_links', 'parents'])
        d['task_defs'] = [task_def.to_dict() for task_def in self.task_defs]
        d['type'] = self.TYPE
        if not any(self.links.values()):  # no links exist, explicitly write empty dict
            d['links'] = {}
        return d

    @classmethod
    def from_dict(cls, d):
        d = copy.deepcopy(d)
        task_def_dicts = d.pop('task_defs')
        task_defs = []
        for td in task_def_dicts:
            task_defs.append(_object_from_dict(td))
        link_dict = d.pop('links', None)
        if link_dict is not None:
            d['links'] = {int(k): v for k, v in link_dict.items()}
        d.pop('type', None)
        return cls(task_defs, **d)

    def __get_task_defs_and_update_links(self):
        """
        Get a list of all TaskDefinition objects in this DAG (new
        instances). Links are updated across nested DAGs
        """
        tasks = []
        for d in self.task_defs:
            if isinstance(d, DAGTask):
                tasks.append(d.__get_task_defs_and_update_links())
            else:
                tasks.append(d.copy())

        self.__apply_links_to_task_defs(tasks)
        tasks = list(_flatten(tasks))
        self.__remove_redundant_links(tasks)
        self._resolved_tasks = tasks
        return tasks

    def __get_p_c_links(self, tasks):
        """Generate (parent: children) dict
        """
        links = {t: [] for t in tasks}
        for t in tasks:
            for pt in t.parents:
                if t not in links[pt]:
                    links[pt].append(t)
        return links

    def __get_c_p_links(self, tasks):
        """Generate (child: parents) dict
        """
        return {t: t.parents for t in tasks}

    def get_task_defs_and_links(self):
        """Get new instances of all task with new links
        """
        task_defs = self.__get_task_defs_and_update_links()
        p_c_links = self.__get_p_c_links(task_defs)
        c_p_links = self.__get_c_p_links(task_defs)
        return task_defs, p_c_links, c_p_links
