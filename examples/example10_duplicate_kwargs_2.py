# -*- coding: utf-8 -*-
"""
Tailor Example 10

This example introduces the following NEW concepts:
    - Specify *kwargs* both in BranchTask and in PythonTasks to be duplicated

When duplicating a DAG, kwargs are passed to all "root" tasks of that
DAG (i.e. those tasks without parents).

A simple DAG (sub_dag) to be duplicated can be illustrated as:

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

Here t1 and t2 are root tasks and will receive kwargs from the duplicate task
as illustrated here:

                          +-------------------------+
                          |        BranchTask       |
                          |                         |
                          |task=sub_dag             |
                          |kwargs=[{k1:v1}, {k2:v2}]|
                          +-------------------------+
                                       |
         +-------------------+---------+--------+-------------------+
         |                   |                  |                   |
         |                   |                  |                   |
+--------v-------+  +--------v-------+  +-------v-------+  +--------v-------+
|      Task (t1) |  |    Task (t2)   |  |   Task (t1)   |  |    Task (t2)   |
| kwargs={k1:v1} |  | kwargs={k1:v1} |  | kwargs={k2:v2}|  | kwargs={k2:v2} |
+--------+-------+  +--------+-------+  +-------+-------+  +--------+-------+
         |                   |                  |                   |
         +---------+---------+                  +---------+---------+
                   |                                      |
          +--------v--------+                    +--------v--------+
          | Task (t3)       |                    | Task (t3)       |
          | parents=[t1,t2] |                    | parents=[t1,t2] |
          +-----------------+                    +-----------------+



"""

from tailor import PythonTask, BranchTask, DAG, Workflow, Project

### workflow definition ###

# task to duplicate (note that no args are specified)
t1 = PythonTask(
    function='builtins.print',
    name='task 1',
    args=['a', 'few', 'arguments']
)
# another task to duplicate, with args
t2 = PythonTask(
    function='builtins.print',
    name='task 2',
    args=['more', 'arguments']
    # args provided to Duplicate will be appended to this list
)
t3 = PythonTask(
    function='builtins.print',
    name='task 3',
    args='Hello from task 3 which got no kwargs from duplicate...',
    parents=[t1, t2]
)

sub_dag = DAG(tasks=[t1, t2, t3], name='sub-dag')

dup = BranchTask(task=sub_dag,
                 name='duplicate',
                 kwargs=[
                     {'sep': ' - ', 'end': '\n\n'},
                     {'sep': ' --- ', 'end': '\n\n\n'}
                 ])

# outer workflow
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
