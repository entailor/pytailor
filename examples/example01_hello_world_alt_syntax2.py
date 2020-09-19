# -*- coding: utf-8 -*-
"""
pyTailor Example 1, alternative syntax 2

Here is the Hello world example with alternative syntax using context managers.
"""

from pytailor import PythonTask, DAG, Project, Workflow

### dag definition ###

with DAG(name='dag') as dag:
    t1 = PythonTask(
        function='builtins.print',
        # function='builtins.abs',  # will raise type error
        name='job 1',
        args=['\nHello, world!\n'],
    )
    t2 = PythonTask(
        function='builtins.print',
        name='job 2',
        args=['\nHello again,', 'world!\n'],
        parents=t1,
    )

# open a project
prj = Project.from_name('Test')

### workflow execution ###

# create a workflow
wf = Workflow(
    project=prj,
    dag=dag,
    name='Hello from Pytailor',
)

# run the workflow
wf.run()

# check the status of the workflow run
print('The workflow finished with state:')
print(wf.state)

### workflow retrieval ###

wf2 = Workflow.from_project_and_id(prj, wf.id)

assert wf.id == wf2.id

# pretty print the workflow
print(wf)
