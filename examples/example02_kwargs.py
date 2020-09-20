# -*- coding: utf-8 -*-
"""
pyTailor Example 2

This example introduces the following NEW concepts:
    - For PythonTasks:
        - Specifying keyword arguments (**kwargs) to the function
"""

from pytailor import PythonTask, DAG, Workflow, Project

### workflow definition ###

with DAG(name="dag") as dag:

    t1 = PythonTask(function="time.sleep", name="task 1", args=[1])
    t2 = PythonTask(
        function="builtins.print",
        name="task 2",
        args=["\nSlept for", "1", "second"],
        kwargs={"sep": "   ", "end": "\n\n"},
        parents=t1,
    )

### workflow run ###

# open a project
prj = Project.from_name("Test")

# create a workflow:
wf = Workflow(project=prj, dag=dag, name="kwarg workflow")

# run the workflow
wf.run()

# check the status of the workflow run
print("The workflow finished with state:")
print(wf.state)
