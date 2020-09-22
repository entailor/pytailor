"""
This script defines and executes a branching workflow and makes assertions for
the expected outputs and files at different scoping levels
"""

from pytailor import PythonTask, BranchTask, DAG, Workflow, Project, FileSet


with DAG(name="DAG") as dag:

    # create some files based on and inputted list of file names
    with BranchTask(
        name="MAKE_FILES", branch_data="<% $.inputs.file_name %>"
    ) as branch1:

        with DAG(name="SUBDAG2"):

            t1 = PythonTask(
                name="T1",
                function="builtins.open",
                args=["<% $.inputs.file_name %>", "a"],
                upload={"outfile": "*"},
            )

            PythonTask(
                function="glob.glob",
                name="T2",
                args=["**/*.txt"],
                kwargs={"recursive": True},
                download="outfile",
                output_to="downloaded_to_T2",
                parents=t1
            )


    t2 = PythonTask(
        name="T3",
        function="builtins.str",
        args=["<% $.files.outfile %>"],
        output_to="output_T3",
        parents=branch1,
    )

    # branch based on created files and existing files
    with BranchTask(
        name="USE_FILES", branch_files=["testfiles", "outfile"], parents=t2
    ) as branch2:

        with DAG(name="SUBDAG2"):

            t4 = PythonTask(
                function="glob.glob",
                name="T4",
                args=["**/*.txt"],
                kwargs={"recursive": True},
                download=["testfiles", "outfile", "inpfile"],
                output_to="downloaded_files",
            )

            PythonTask(
                name="T5",
                function="builtins.str",
                args=["<% $.outputs.downloaded_files %>"],
                output_to="output_T5",
                parents=t4,
            )


# open a project
prj = Project.from_name("Test")

# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(
    testfiles=["testfiles/testfile_01.txt", "testfiles/testfile_02.txt"],
    inpfile=["testfiles/testfile_03.txt"],
)

# inputs
inputs = {"file_name": ["file1.txt", "file2.txt"]}

# create a workflow
wf = Workflow(
    project=prj, dag=dag, name="file branching test", fileset=fileset, inputs=inputs
)

# run the workflow
wf.run(distributed=True, worker_name='test_worker')
# wf.run()
