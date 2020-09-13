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

from tailor import PythonTask, BranchTask, DAG, Workflow, Project, FileSet

### workflow definition ###

t1 = PythonTask(
    function='builtins.list',
    name='task 1',
    download='testfiles',
    upload={'outfiles': '*.txt'}
)

t2 = PythonTask(
    function='builtins.print',
    name='task 2',
    args=['<% $.files.outfiles[0] %>'],
    download='outfiles'
)

branch = BranchTask(
    task=t2,
    name='branch',
    branch_data=['<% $.files.outfiles %>'],
    branch_files=['outfiles'],
    parents=t1
)


dag = DAG(tasks=[t1, branch], name='dag')

### workflow run ###

# open a project
project_uuid = "702d688e-972d-4580-afa2-fc616533ccba"
prj = Project(project_uuid)

# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(testfiles=['testfiles/testfile_01.txt', 'testfiles/testfile_02.txt'])

inputs = {
    # 'data': [1, 2, 3],
    'data': {0: 'a', 1: 'b', 2: 'c'},
    'other': 'asdf',
    'values': [1, 2, 3]
}

# create a workflow:
wf = Workflow(
    project=prj,
    dag=dag,
    name='branch workflow 2',
    inputs=inputs,
    fileset=fileset
)

# run the workflow
wf.run()

# check the status of the workflow
print('The workflow finished with state:')
print(wf.state)
