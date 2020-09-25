from pytailor import PythonTask, BranchTask, DAG, Workflow, Project


with DAG() as dag:
    with BranchTask(branch_data="<% $.inputs.data1 %>"):
        with DAG():
            t1 = PythonTask(
                name="Create files",
                function="builtins.open",
                args=["T1.FEM", "a"],
                upload={"mesh": "*.FEM"}
            )
            with BranchTask(branch_data="<% $.inputs.data2 %>",
                            parents=t1):
                PythonTask(
                    function="glob.glob",
                    name="Use files",
                    args=["**/*.FEM"],
                    kwargs={"recursive": True},
                    download="mesh",
                    output_to="downloaded"
                )

# open a project
prj = Project.from_name("Test")

# inputs
inputs = {"data1": [0, 1],
          "data2": [2, 3]}

# create a workflow
wf = Workflow(
    project=prj,
    dag=dag,
    name="scope inheritance test",
    inputs=inputs
)

# run the workflow
# wf.run(distributed=True, worker_name='test_worker')
wf.run()

target_outputs = {
    'downloaded': {'0': {'0': ['mesh\\0\\0\\T1.FEM'], '1': ['mesh\\0\\1\\T1.FEM']},
                   '1': {'0': ['mesh\\1\\0\\T1.FEM'], '1': ['mesh\\1\\1\\T1.FEM']}}
}

assert wf.outputs == target_outputs
