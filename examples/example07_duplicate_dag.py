# -*- coding: utf-8 -*-
"""
pyTailor Example 7

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

with DAG(name='dag') as dag:
    with BranchTask(
            name='branch',
            branch_data=['<% $.files.testfiles %>'],
            branch_files=['testfiles']):
        with DAG(name='sub-dag') as sub_dag:
            t1 = PythonTask(
                function='glob.glob',
                name='task 2',
                args=['**/*.txt'],
                kwargs={'recursive': True},
                download='testfiles',
                output_to='glob_res')
            PythonTask(
                function='builtins.print',
                name='task 3',
                args=['<% $.files.testfiles %>', '<% $.outputs.glob_res %>'],
                parents=t1)

### workflow run ###

# open a project
project_uuid = "702d688e-972d-4580-afa2-fc616533ccba"
prj = Project(project_uuid)

# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(testfiles=['testfiles/testfile_01.txt', 'testfiles/testfile_02.txt'])

inputs = {}

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
