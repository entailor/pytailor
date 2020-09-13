# -*- coding: utf-8 -*-
"""
Tailor Example 6

This example introduces the following NEW concepts:
    - Use BranchTask to duplicate a single PythonTask
    - For BranchTask definitions:
        - Usage of the *args* argument

The principle for duplication using the *args* argument can be illustrated by
the following schematics:

                +-----------+
                | Duplicate |
                |           |
                | task=t1   |
                | args=[1,2]|
                +-----------+
                      |
            +------------------+
            |                  |
      +-----v-----+      +-----v-----+
      | Task (t1) |      | Task (t1) |
      |  args=[1] |      |  args=[2] |
      +-----------+      +-----------+

Duplicated tasks always become children of the BranchTask that created them.

"""

from tailor import PythonTask, BranchTask, DAG, Workflow, Project

### workflow definition ###

# task to duplicate (note that no args are specified)
t1 = PythonTask(
    function='builtins.print',
    name='task 1',
    args=['<% $.inputs.data %>', '<% $.inputs.other %>']
)

branch = BranchTask(
    task=t1,
    name='duplicate',
    branch_data=['<% $.inputs.data %>']
)

dag = DAG(tasks=branch, name='dag')

### workflow run ###

# open a project
project_uuid = "702d688e-972d-4580-afa2-fc616533ccba"
prj = Project(project_uuid)

inputs = {
    # 'data': [1, 2, 3],
    'data': {0: 'a', 1: 'b', 2: 'c'},
    'other': 'asdf'
}

# create a workflow:
wf = Workflow(
    project=prj,
    dag=dag,
    name='branch workflow',
    inputs=inputs
)

# run the workflow
wf.run()

# check the status of the workflow
print('The workflow finished with state:')
print(wf.state)