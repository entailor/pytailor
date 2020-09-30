from __future__ import annotations

from typing import Optional

from pytailor.exceptions import ParameterizationError


class Parameterization:
    def __init__(self, name: str, parent: Optional[Parameterization] = None):
        self.__name = name
        self.__parent = parent
        self.__items = {}

    def __getattr__(self, name):
        if not name.startswith("__"):
            setattr(self, name, Parameterization(name, self))
        return getattr(self, name)

    def __getitem__(self, item):
        if item in self.__items:
            return self.__items[item]
        else:
            if not isinstance(item, int):
                raise TypeError(
                    "Only integer indices allowed. Use dot-notation for"
                    "key/value data"
                )
            parametrization = Parameterization(self.__name + f"[{item}]", self.__parent)
            self.__items[item] = parametrization
            return parametrization

    def get_query(self):
        query = self.__name
        parent = self.__parent
        while parent:
            query = parent.__name + "." + query
            parent = parent.__parent
        return f"<% $.{query} %>"

    def get_name(self):
        return self.__name

    def __deepcopy__(self, memo):
        return self

    def check_is_legal_name_ref(self, arg_name: str = None):
        # Parameterization objects are used to generate names for use with
        # 'output_to', 'output_extaction', 'upload' and 'download'. In these
        # cases the corresponding query must resolve to the form $.outputs.<name>.
        # or $.files.<name>
        # I.e. a single name on the first level. And without indexing.
        if not (self.__name.isidentifier() and self.__parent.__parent is None):
            error_msg = "Illegal parameter reference."
            if arg_name:
                error_msg += (
                    f" When specifying parameter name for '{arg_name}' "
                    f"format <parameterization_obj>.<parameter_name> must be"
                    f" used."
                )
            raise ParameterizationError(error_msg)


class Inputs(Parameterization):
    """
    Helper object for **inputs** parameterization.

    **Basic usage**

    ``` python
    from pytailor import PythonTask, DAG, Inputs, Workflow, Project

    inputs = Inputs()

    with DAG() as dag:
        PythonTask(
            function='builtins.print',
            args=inputs.hello,
        )

    prj = Project.from_name("Test")

    wf = Workflow(
        dag=dag,
        project=prj,
        inputs={"hello": ["Hello, world!"]}
    )

    wf.run()
    ```
    """

    def __init__(self):
        super().__init__(name="inputs")


class Outputs(Parameterization):
    """
    Helper object for **outputs** parameterization.

    **Basic usage**

    ``` python
    from pytailor import PythonTask, DAG, Outputs, Workflow, Project

    outputs = Outputs()

    with DAG() as dag:
        t1 = PythonTask(
            function='os.getcwd',
            output_to=outputs.curdir
        )
        PythonTask(
            function='builtins.print',
            args=[outputs.curdir],
        )

    prj = Project.from_name("Test")

    wf = Workflow(
        dag=dag,
        project=prj,
    )

    wf.run()

    print(wf.outputs)

    ```
    """

    def __init__(self):
        super().__init__(name="outputs")


class Files(Parameterization):
    """
    Helper object for **files** parameterization.

    **Basic usage**

    ``` python
    from pytailor import PythonTask, DAG, Files, Workflow, Project, FileSet

    files = Files()

    with DAG() as dag:
        PythonTask(
            function='builtins.print',
            args=["This tasks download the file:", files.inpfile[0]],
            download=files.inpfile
        )

    prj = Project.from_name("Test")

    fileset = FileSet(project=prj)
    fileset.upload(inpfile=["my_file.txt"])

    wf = Workflow(
        dag=dag,
        project=prj,
        fileset=fileset
    )

    wf.run()
    ```
    """

    def __init__(self):
        super().__init__(name="files")
