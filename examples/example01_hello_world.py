# -*- coding: utf-8 -*-
"""
Backend Example 1

This is the Hello world example for tailor.

This example introduces the following NEW concepts:
    - Create PythonTasks and DAGs
    - For PythonTasks:
        - Specifying the function to run (must be an importable python function)
        - Specifying a name for the job
        - Specifying positional arguments (*args) to the function
        - Specifying relationships between tasks
    - For DAGs:
        - Specifying which tasks are part of the DAG
        - Specifying a name for the DAG
    - Create a Workflow and run it in 'here_and_now' mode
    - Check status of the resulting Workflow after execution
    - Retrieve a workflow from the backend into a new Workflow object
"""

from tailor import PythonTask, DAG, Project, Workflow

### dag definition ###

t1 = PythonTask(
    function='builtins.print',
    # function='builtins.abs',  # will raise type error
    name='job 1',
    args='\nHello, world!\n',  # equivalent to ['\nHello, world!\n']
)
t2 = PythonTask(
    function='builtins.print',
    name='job 2',
    args=['\nHello again,', 'world!\n'],
    parents=t1
)

dag = DAG(tasks=[t1, t2], name='dag')

# prj = Project.from_name('Test')
prj = Project('702d688e-972d-4580-afa2-fc616533ccba')

### workflow execution ###

# create a workflow
wf = Workflow(
    project=prj,
    dag=dag,
    name='Hello from Pytailor',
)

# run the workflow
wf.run(mode='here_and_now')

# check the status of the workflow run
print(wf.state)


### workflow retrieval ###

wf2 = Workflow.from_project_and_id(prj, wf.id)

assert wf.id == wf2.id
