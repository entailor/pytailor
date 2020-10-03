from pytailor import PythonTask, BranchTask, DAG, Inputs, Outputs, Files
import engineering_tasks

inputs = Inputs()
outputs = Outputs()
files = Files()

with DAG(name="File branching test") as dag:
    t1 = PythonTask(
        name="Pre-processing 1",
        function=engineering_tasks.prepare_simulation_data,
        kwargs={"parameters": inputs.pre_proc_data, "base_file": files.base_file},
        download=files.base_file,
        upload={files.inp_file: "sim_inp_file_*.inp"},
    )
    with BranchTask(
        name="Branching 1", branch_files=files.inp_file, parents=t1
    ) as branch:
        with DAG(name="Sub dag"):

            t2 = PythonTask(
                name="Pre-processing 2",
                function=engineering_tasks.prepare_simulation_data,
                kwargs={
                    "parameters": inputs.pre_proc_data2,
                    "base_file": files.base_file,
                },
                download=files.base_file,
                upload={files.inp_file2: "sim_inp_file_*.inp"},
            )

            with BranchTask(
                name="Branching 2", branch_files=files.inp_file2, parents=t2
            ) as branch2:
                PythonTask(
                    name="Simulation",
                    function=print,
                    args=[files.inp_file[0]],
                )

    PythonTask(
        name="Post-processing",
        function=engineering_tasks.post_process_simulation_data,
        args=[files.res_file],
        download=files.res_file,
        upload={files.report: "report.pdf"},
        output_to=outputs.essential_results,
        parents=branch,
    )

### run workflow ###

from pytailor import Project, FileSet, Workflow

# open a project
prj = Project.from_name("Test")

# define inputs
workflow_inputs = {
    "pre_proc_data": [
        {"param1": 0},
        {"param1": 1},
        {"param1": 2},
        {"param1": 3},
        {"param1": 4},
    ],
    "pre_proc_data2": [
        {"param1": 0},
        {"param1": 1},
        {"param1": 2},
        {"param1": 3},
        {"param1": 4},
    ],
}

# prepare inputs files
# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(base_file=["testfiles/testfile.inp"])


# create a workflow:
wf = Workflow(
    project=prj,
    dag=dag,
    name="simulation workflow",
    inputs=workflow_inputs,
    fileset=fileset,
)

# run the workflow
wf.run(distributed=True)
