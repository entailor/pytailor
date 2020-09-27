# -*- coding: utf-8 -*-
"""
pyTailor Example 5
"""

from pytailor import PythonTask, DAG, Workflow, Project, FileSet
from pytailor.api.parameterization import Outputs, Files

### workflow definition ###

files = Files()
outputs = Outputs()

with DAG(name="dag") as dag:

    t1 = PythonTask(
        function="glob.glob",
        name="task 1",
        args=["**/*.txt"],
        kwargs={"recursive": True},
        download=files.testfiles,  # refers to a file tag
        output_to=outputs.downloaded_files,  # put function's return value on outputs.downloaded_files
    )
    t2 = PythonTask(
        function="shutil.copyfile",
        name="task 2",
        args=[files.inpfile[0], "newfile.txt"],
        download=files.inpfile,
        upload={files.outfile: "newfile.txt"},
    )
    t3 = PythonTask(
        function="builtins.print",
        name="task 3",
        args=["Downloaded", files.outfile],
        download="outfile",
        parents=t2,
    )

### workflow run ###

# open a project
prj = Project.from_name("Test")

# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(
    testfiles=["testfiles/testfile_01.txt", "testfiles/testfile_02.txt"],
    inpfile=["testfiles/testfile_03.txt"],
)


# create a workflow:
wf = Workflow(project=prj, dag=dag, name="files workflow", fileset=fileset)

# run the workflow
wf.run()

# check the status of the workflow
print("The workflow finished with state:")
print(wf.state)

# print the output of task 1
print("Downloaded files:\n", wf.outputs.get("downloaded_files"))
