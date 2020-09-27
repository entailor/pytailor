# -*- coding: utf-8 -*-
"""
pyTailor Example 4
"""

from pytailor import PythonTask, DAG, Workflow, Project
from pytailor.api.parameterization import Outputs

### workflow definition ###

outputs = Outputs()

with DAG(name="dag") as dag:

    t1 = PythonTask(
        function="glob.glob",
        name="task 1",
        args=["../*.py"],
        output_to=outputs.parentdir_content,  # form 1: single string
    )
    t2 = PythonTask(
        function="os.getcwd",
        name="task 2",
        output_extraction={outputs.curdir: "<% $ %>"},  # form 2: (tag: query) dict
    )
    t3 = PythonTask(
        function="builtins.print",
        name="task 3",
        args=[
            "Python files in parent dir (as list):",
            outputs.parentdir_content,
            "Current working dir:",
            outputs.curdir,
        ],
        kwargs={"sep": "\n\n", "end": "\n\n"},
        parents=[t1, t2],
    )

### run workflow ###

# open a project
prj = Project.from_name("Test")

# create a workflow:
wf = Workflow(project=prj, dag=dag, name="outputs workflow")

# run the workflow
wf.run()

# check the status of the workflow
print("The workflow finished with state:")
print(wf.state)

# outputs are available on the run object
print("Outputs are:")
print(wf.outputs)
