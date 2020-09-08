# -*- coding: utf-8 -*-
"""
Backend Example 2

This example introduces the following NEW concepts:
    - For PythonTasks:
        - Specifying keyword arguments (**kwargs) to the function
"""

from tailor import PythonTask, DAG, Workflow, Project

### workflow definition ###

t1 = PythonTask(
    function='time.sleep',
    name='task 1',
    args=[1]
)
t2 = PythonTask(
    function='builtins.print',
    name='task 2',
    args=['\nSlept for', '1', 'second'],
    kwargs={'sep': '   ', 'end': '\n\n'},
    parents=t1
)

dag = DAG(tasks=[t1, t2], name='dag')

### workflow run ###

# open a project
project_uuid = "702d688e-972d-4580-afa2-fc616533ccba"
prj = Project(project_uuid)

# create a workflow:
wf = Workflow(project=prj, dag=dag, name='kwarg workflow')

# run the workflow
wf.run()

# check the status of the workflow run
print('The workflow finished with state:')
print(wf.state)
