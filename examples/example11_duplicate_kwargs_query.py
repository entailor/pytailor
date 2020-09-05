# -*- coding: utf-8 -*-
"""
Tailor Example 11

This example introduces the following NEW concepts:
    - For BranchTasks:
        - Use a query expression for the *kwargs* argument

"""

from tailor import PythonTask, BranchTask, DAG, Workflow, Project

### workflow definition ###

t1 = PythonTask(
    function='builtins.print',
    name='task 1',
    args=['a', 'few', 'arguments'],
    kwargs={'sep': ' -- '}  # kwargs are provided both here and in Duplicate
)

# alt 1: single query expression
dup1 = BranchTask(task=t1, name='duplicate', kwargs='<% $.inputs.kwargs %>')

# alt 2: list of query expressions, same behaviour
dup2 = BranchTask(task=t1, name='duplicate',
                  kwargs=['<% $.inputs.kwargs[0] %>', '<% $.inputs.kwargs[1] %>'])

dag = DAG(tasks=[dup1, dup2], name='dag')

### workflow run ###

# open a project
project_uuid = "702d688e-972d-4580-afa2-fc616533ccba"
prj = Project(project_uuid)

inputs = {
    'kwargs': [
        {'end': '\n\n'},
        {'end': '\n\n\n'}
    ]
}

# create a workflow:
wf = Workflow(project=prj, dag=dag, name='duplicate workflow',
              inputs=inputs)

# run the workflow
wf.run()

# check the status of the workflow
print('The workflow finished with state:')
print(wf.state)
