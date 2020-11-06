from pytailor import PythonTask, BranchTask, DAG, Workflow, Project

with DAG() as dag:
    with BranchTask(branch_data="<% $.inputs.data1 %>"):
        with DAG():
            t1 = PythonTask(
                name="Create files 1",
                function="builtins.open",
                args=["T1.FEM", "a"],
                upload={"mesh1": "*.FEM"},
            )
            t2 = PythonTask(
                name="Create files 2",
                function="builtins.open",
                args=["T2.FEM", "a"],
                upload={"mesh2": "*.FEM"},
            )
            with BranchTask(branch_data="<% $.inputs.data2 %>", parents=[t1, t2]):
                PythonTask(
                    function="glob.glob",
                    name="Use files",
                    args=["**/*.FEM"],
                    kwargs={"recursive": True},
                    download=["mesh1", "mesh2"],
                    output_to="downloaded",
                )

# open a project
prj = Project.from_name("Test")

# inputs
inputs = {"data1": [0, 1], "data2": [2, 3]}

# create a workflow
wf = Workflow(project=prj, dag=dag, name="scope inheritance test", inputs=inputs)

target_outputs = {
    "downloaded": {
        "0": {
            "0": ["mesh1\\0\\0\\T1.FEM", "mesh2\\0\\0\\T2.FEM"],
            "1": ["mesh1\\0\\0\\T1.FEM", "mesh2\\0\\0\\T2.FEM"],
        },
        "1": {
            "0": ["mesh1\\1\\0\\T1.FEM", "mesh2\\1\\0\\T2.FEM"],
            "1": ["mesh1\\1\\0\\T1.FEM", "mesh2\\1\\0\\T2.FEM"],
        },
    }
}
