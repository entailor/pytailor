from pytailor import DAG, BranchTask, PythonTask, Project, FileSet, Workflow

import glob


# use an "inline" function, workflow cannot be run in distributed mode.
def print_downloaded_files():
    print(glob.glob("**/*.txt", recursive=True))


with DAG(name="dag") as dag:
    with BranchTask(
        name="branch",
        branch_files=["real_files", "imag_files"],
    ):
        with DAG(name="sub-dag") as sub_dag:
            PythonTask(
                function=print_downloaded_files,
                name="task 1",
                download=["real_files", "imag_files"]
            )


### workflow run ###

# open a project
prj = Project.from_name("Test")

# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(
    real_files=["testfiles/testfile_01.txt", "testfiles/testfile_02.txt"],
    imag_files=["testfiles/testfile_03.txt", "testfiles/testfile_04.txt"],
)


# create a workflow:
wf = Workflow(project=prj, dag=dag, name="files workflow", fileset=fileset)

# run the workflow
wf.run()
