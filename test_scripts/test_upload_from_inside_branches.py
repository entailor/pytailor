from pytailor import PythonTask, BranchTask, DAG, Workflow, Project, FileSet

### workflow definition ###

with DAG(name="dag") as dag:
    with BranchTask(name="duplicate1", branch_data=["<% $.inputs.data1 %>"]):
        with DAG(name="subdag"):
            t1 = PythonTask(
                name="T1",
                function="builtins.open",
                args=["file_level1.txt", "a"],
                upload={"outfile_level1": "*"},
            )

            with BranchTask(name="duplicate2", branch_data=["<% $.inputs.data2 %>"],
                            parents=t1):
                with DAG(name="subsubdag"):
                    t2 = PythonTask(
                        name="T2",
                        function="builtins.open",
                        args=["file_level2.txt", "a"],
                        upload={"outfile_level2": "*"},
                    )
                    with BranchTask(name="duplicate3",
                                    branch_data=["<% $.inputs.data3 %>"],
                                    parents=t2):
                        t3 = PythonTask(
                            name="T3",
                            function="builtins.open",
                            args=["file_level3.txt", "a"],
                            upload={"outfile_level3": "*"},
                        )

### workflow run ###

# open a project
prj = Project.from_name("Test")

inputs = {
    "data1": [1, 2],
    "data2": [11, 22],
    "data3": [111, 222],
}

# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(
    testfiles=["testfiles/testfile_01.txt", "testfiles/testfile_02.txt"],
    inpfile=["testfiles/testfile_03.txt"],
)

# create a workflow:
wf = Workflow(project=prj, dag=dag, name="upload from branch workflow", inputs=inputs,
              fileset=fileset)

# run the workflow
wf.run()

# check the status of the workflow
print("The workflow finished with state:")
print(wf.state)

assert wf.state == "COMPLETED"

# cleanup
prj.delete_workflow(wf.id)
