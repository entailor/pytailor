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

from tailor import PythonTask, BranchTask, DAG, Workflow, Project, FileSet

### workflow definition ###


# task to duplicate (note that no args are specified)
t1 = PythonTask(
    function='builtins.print',
    name='task 1',
    args=['<% $.inputs.data1 %>']
)
t2 = PythonTask(
    function='builtins.print',
    name='task 2',
    args=['This is a regular argument'],
    parents=t1,
    download='testfiles'
)
t3 = PythonTask(
    function='builtins.print',
    name='task 3',
    args=['<% $.inputs.other %>', '<% $.inputs.data2 %>'],
    parents=t2
)

sub_dag = DAG(tasks=[t1, t2, t3], name='sub-dag')

dup = BranchTask(
    task=sub_dag, name='duplicate',
    branch_data=['<% $.inputs.data1 %>', '<% $.inputs.data2 %>'],
    branch_files=['testfiles']
)

# outer workflow
dag = DAG(tasks=dup, name='dag')

### workflow run ###

# open a project
project_uuid = "702d688e-972d-4580-afa2-fc616533ccba"
prj = Project(project_uuid)

# inputs
inputs = {
    'data1': [1, 2, 3],
    'data2': [4, 5, 6],
    'other': 'a string',
}

# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(testfiles=[
    'testfiles/testfile_01.txt',
    'testfiles/testfile_02.txt',
    'testfiles/testfile_03.txt'
])

# create a workflow:
wf = Workflow(
    project=prj,
    dag=dag,
    name='branch workflow with dag',
    inputs=inputs,
    fileset=fileset
)

# run the workflow
wf.run()

# check the status of the workflow
print('The workflow finished with state:')
print(wf.state)

# pretty print
print(wf)
