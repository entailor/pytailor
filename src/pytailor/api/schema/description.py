import importlib
import inspect
import sys
# from pytailor.api.dag import DAG


class Description:
    """
     Workflow definition description generator to define workflow definition

    **Basic usage**

    ``` python

    wf_def_description = "This example explains branchtasks"
    wf_def_name = "branch task example"
    from pytailor import PythonTask, BranchTask, DAG

    with DAG(name="duplicate dag example") as dag:
        with BranchTask(
            name="branch",
            branch_data=["<% $.files.testfiles %>"],
            branch_files=["testfiles"],
        ):
            with DAG(name="sub-dag") as sub_dag:
                t1 = PythonTask(
                    function="glob.glob",
                    name="task 2",
                    args=["**/*.txt"],
                    kwargs={"recursive": True},
                    download="testfiles",
                    output_to="glob_res",
                )
                PythonTask(
                    function="builtins.print",
                    name="task 3",
                    args=["<% $.files.testfiles %>", "<% $.outputs.glob_res %>"],
                    parents=t1,
                )
    description = Description.from_dag(dag, wf_def_name=wf_def_name,
                                       wf_def_description=wf_def_description
    )
    ```
    **Parameters**

    - **name** (dict)
        Specify a name for the workflow definition
    - **description_string** (str)
        Specify a description string in markdown format

    """

    _string = None

    def __init__(self, name: str = None, description_string: str = None):
        self.string = "" or description_string
        self.name = "" or name

    def to_string(self):
        return self.string

    def to_markdown(self, filename="Readme.MD"):
        with open(filename, "w") as text_file:
            text_file.write(self.string)

    @property
    def string(self):
        return self._string

    @string.setter
    def string(self, string):
        assert isinstance(string, str), "description_string must be a string"
        self._string = string

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        assert isinstance(name, str), "name must be a string"
        self._name = name

    @classmethod
    def from_dag(cls, dag, wf_def_name="", wf_def_description=""):
        """
        Generates a workflow definition description from a pytailor DAG class

        **Parameters**

        - **dag** (DAG)
            Specify your DAG for workflow definition
        - **wf_def_name** (str)
            Specify a name for workflow definition
        - **wf_def_description** (str)
            Specify an overall description, what are the main objectives of your workflow definition?
            What are the main steps in the DAG?

        """

        all_tasks = cls.get_all_tasks(dag.to_dict(), [])

        if wf_def_description:
            description = wf_def_description
        else:
            description = """
               template Workflow description

               This is a rendering of the description string at the level of the dag.

               All other strings in this document are auto generated from docstrings in
               the code and renderings of the dag implementation 

               """

        readme = [
            f"# Workflow: {wf_def_name}",
            "\n\n",
            description,
            "\n\n",
            "## Tasks in this workflow",
            "\n\n",
        ]

        for task in all_tasks[1:]:
            name = task.get("name", "task name missing")
            task_type = task["type"]
            my_class = cls.get_class(task_type)
            readme.append(f"### {name} ({task_type} type)\n\n")
            readme.append(f"#### Task implementation:\n\n")
            for key, value in task.items():
                for annotation in my_class.__init__.__annotations__.keys():
                    if key == annotation:
                        if key not in ["name", "task"]:
                            readme.append(f"    {key}: {value}\n")
                            if key == "function":
                                readme.append(f"#### Function docstring:\n\n")
                                readme.append(cls.get_docstring(value) + "\n\n")

        return cls(wf_def_name, "".join(readme))

    @classmethod
    def get_all_tasks(cls, dag_dict, all_tasks):
        if isinstance(dag_dict, dict):
            all_tasks.append(dag_dict)
        if dag_dict.get("tasks"):
            for task in dag_dict["tasks"]:
                cls.get_all_tasks(task, all_tasks)
        if dag_dict.get("task"):
            if dag_dict["task"].get("tasks"):
                for task in dag_dict["task"]["tasks"]:
                    cls.get_all_tasks(task, all_tasks)
            else:
                cls.get_all_tasks(dag_dict["task"], all_tasks)
        return all_tasks

    @staticmethod
    def get_docstring(function):
        import_string = function.rsplit(".", 1)
        docstring = (
            importlib.import_module(import_string[0])
            .__dict__.get(import_string[1])
            .__doc__
        )
        if docstring:
            return docstring
        else:
            return f"\nNo docstring provided for function {function}\n"

    @staticmethod
    def get_class(task_type):
        cls_members = inspect.getmembers(
            sys.modules["pytailor.api.dag"], inspect.isclass
        )
        for cls_member in cls_members:
            if cls_member[1].__dict__.get("TYPE"):
                try:
                    if cls_member[1].TYPE.name.lower() == task_type.lower():
                        return cls_member[1]
                except AttributeError:
                    pass
