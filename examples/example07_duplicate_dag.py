# -*- coding: utf-8 -*-
"""
Tailor Example 7

This example introduces the following NEW concepts:
    - Use the BranchTask to duplicate a DAG
    - Specify *args* both in Duplicate and in tasks to be duplicated

When branching a DAG, *args* are passed to all "root" tasks of that
dag (i.e. those tasks without parents).

A simple dag (sub_dag) to be duplicated can be illustrated as:

+-----------+       +-----------+
| Task (t1) |       | Task (t2) |
|           |       |           |
+-----+-----+       +-----+-----+
      |                   |
      +---------+---------+
                |
       +--------v--------+
       | Task (t3)       |
       | parents=[t1,t2] |
       +-----------------+

Here t1 and t2 are root tasks and will receive args from the duplicate task as
illustrated here:

                              +------------+
                              | BranchTask |
                              |            |
                              | task=sub_wf|
                              | args=[1,2] |
                              +-----+------+
                                    |
      +-------------------+---------+--------+-------------------+
      |                   |                  |                   |
      |                   |                  |                   |
+-----v-----+       +-----v-----+      +-----v-----+       +-----v-----+
| Task (t1) |       | Task (t2) |      | Task (t1) |       | Task (t2) |
| args=[1]  |       | args=[1]  |      | args=[2]  |       | args=[2]  |
+-----+-----+       +-----+-----+      +-----+-----+       +-----+-----+
      |                   |                  |                   |
      +---------+---------+                  +---------+---------+
                |                                      |
       +--------v--------+                    +--------v--------+
       | Task (t3)       |                    | Task (t3)       |
       | parents=[t1,t2] |                    | parents=[t1,t2] |
       +-----------------+                    +-----------------+

When *args* are  already specified on task(s) which will receive *args* from
the DuplicateTask, the args already present will be overwritten.

"""

from tailor import PythonTask, BranchTask, DAG, Workflow, Project

### workflow definition ###


# task to duplicate (note that no args are specified)
t1 = PythonTask(
    function='builtins.print',
    name='task 1',
)
t2 = PythonTask(
    function='builtins.print',
    name='task 2',
    args=['This arg will be overwritten by the DuplicateTask']
)
t3 = PythonTask(
    function='builtins.print',
    name='task 3',
    args='Hello from task 3 which got no args from duplicate...',
    parents=[t1, t2]
)

sub_dag = DAG(tasks=[t1, t2, t3], name='sub-dag')

dup = BranchTask(task=sub_dag, name='duplicate',
                 args=['Duplicated 1', 'Duplicated 2'])

# outer workflow
dag = DAG(tasks=dup, name='dag')

### workflow run ###

# open a project
project_uuid = "702d688e-972d-4580-afa2-fc616533ccba"
prj = Project(project_uuid)

# create a workflow:
wf = Workflow(project=prj, dag=dag, name='duplicate workflow')

# run the workflow
wf.run()

# check the status of the workflow
print('The workflow finished with state:')
print(wf.state)

# pretty print
print(wf)
