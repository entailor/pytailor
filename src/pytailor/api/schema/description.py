import importlib


class Description:

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
            readme.append(f"### {task_type}: {name}\n\n")
            readme.append(f"#### Task implementation:\n\n")
            for key, value in task.items():
                if key == "args":
                    readme.append(f"    args: {value}\n")
                if key == "kwargs":
                    readme.append(f"    kwargs: {value}\n")
                if key == "download":
                    readme.append(f"    download: {value}\n")
                if key == "branch_data":
                    readme.append(f"    branch_data: {value}\n")
                if key == "branch_files":
                    readme.append(f"    branch_files: {value}\n")
                if key == "function":
                    readme.append(f"    function: {value}\n")
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