# -*- coding: utf-8 -*-
"""
Tailor Example 9

This example introduces the following NEW concepts:
    - For BranchTasks:
        - Usage of the *kwargs* argument

The principle for duplication using the *kwargs* argument can be illustrated by
the following schematics:

                +---------------------------+
                |         BranchTask        |
                |                           |
                | task=t1                   |
                | kwargs=[{k1:v1}, {k2:v2}] |
                +---------------------------+
                              |
                 +-----------------------+
                 |                       |
        +--------v-------+      +--------v--------+
        | Task (t1)      |      | Task (t1)       |
        | kwargs={k1:v1} |      |  kwargs={k2:v2} |
        +----------------+      +-----------------+

"""

from tailor import PythonTask, BranchTask, DAG, Workflow, Project

### workflow definition ###

# task to duplicate (note that no kwargs are specified)
t1 = PythonTask(
    function='builtins.print',
    name='task 1',
    args=['foo', 'bar']
)
dup = BranchTask(task=t1,
                 name='duplicate',
                 kwargs=[
                     {'sep': ' - ', 'end': '\n\n'},
                     {'sep': ' --- ', 'end': '\n\n\n'}
                 ])

dag = DAG(tasks=dup, name='dag')

### workflow run ###

# open a project
project_uuid = "702d688e-972d-4580-afa2-fc616533ccba"
prj = Project(project_uuid)

# create a workflow:
wf = Workflow(prj, dag=dag, name='duplicate workflow')

# run the workflow
wf.run()

# check the status of the workflow
print('The workflow finished with state:')
print(wf.state)
