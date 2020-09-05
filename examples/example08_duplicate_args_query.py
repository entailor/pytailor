# -*- coding: utf-8 -*-
"""
Tailor Example 8

This example introduces the following NEW concepts:
    - For BranchTask:
        - Use a query expression for the *args* argument

"""

from tailor import PythonTask, BranchTask, DAG, Workflow, Project

### workflow definition ###

t1 = PythonTask(
    function='builtins.print',
    name='task 1',
)

# alt 1: a single query expression, the args expression is evaluated prior to duplication.
dup1 = BranchTask(task=t1, name='duplicate', args='<% $.inputs.values %>')

# alt 2: a list of query expressions, one duplicated task is created per expression in the
# list. Expressions are evaluated in each duplicate
dup2 = BranchTask(task=t1, name='duplicate',
                  args=['<% $.inputs.values[0] %>', '<% $.inputs.values[1] %>'])

dag = DAG(tasks=[dup1, dup2], name='dag')

### workflow run ###

# open a project
project_uuid = "702d688e-972d-4580-afa2-fc616533ccba"
prj = Project(project_uuid)

inputs = {
    'values': [['dup1_arg1', 'dup1_arg2'], ['dup2_arg1', 'dup2_arg2']]
}

# create a workflow:
wf = Workflow(project=prj, dag=dag, name='duplicate workflow',
              inputs=inputs)

# run the workflow
wf.run()

# check the status of the workflow
print('The workflow finished with state:')
print(wf.state)
