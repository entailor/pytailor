# -*- coding: utf-8 -*-
"""
Backend Example 5

This example introduces the following NEW concepts:
    - For task definitions:
        - Specifying files to download before running the task
        - Specifying files to upload after task is run
    - Specify which local files to upload when a workflow is created

The *download* argument to task can be a single file tag (str) or a list of file
tags. These file tags refer to files in the fileset associated with
the workflow.

To send input files into a workflow the following steps are taken:
    1. Instantiate a FileSet object
    2. Upload files to the fileset with an associated tag
    3. Pass the fileset along when instantiating the workflow
    4. Tasks will now download files by referencing the file tags.

The *upload* argument to Task is used to specify files to send back to the
fileset after a task has been run. *upload* must be a dict of (tag: val),
where val can be:
    1. one or more query expressions(str and list of str) which is applied
       to the function output. The query result is then searched for actual files,
       these files are then uploaded to storage under the given tag.
    2. one or more glob-style strings (str and list of str) which is applied
       in the task's working dir. Matching files are uploaded under the
       given tag.

File *names* can be accessed with queries: "<% $.files.<tag> %>" which is useful when e.g
file name(s) are input to functions.
"""

from tailor import PythonTask, DAG, Workflow, Project, FileSet

### workflow definition ###

t1 = PythonTask(
    function='glob.glob',
    name='task 1',
    args=['*'],
    download='testfiles',  # refers to a file tag
    output_to='downloaded_files'
)
t2 = PythonTask(
    function='shutil.copyfile',
    # function='builtins.print',
    name='task 2',
    args=['<% $.files.inpfile[0] %>', 'newfile.txt'],  # inpfile is a tag
    download='inpfile',
    upload={'outfile': 'newfile.txt'}
)
t3 = PythonTask(
    function='builtins.print',
    name='task 3',
    args=['Downloaded', '<% $.files.outfile %>'],
    download='outfile',
    parents=t2
)

dag = DAG(tasks=[t1, t2, t3], name='dag')
# dag = DAG(tasks=[t1, t2], name='dag')

### workflow run ###

# open a project
project_uuid = "702d688e-972d-4580-afa2-fc616533ccba"
prj = Project(project_uuid)

# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(testfiles=['testfiles/testfile_01.txt', 'testfiles/testfile_02.txt'],
               inpfile=['testfiles/testfile_03.txt']
               )


# create a workflow:
wf = Workflow(project=prj, dag=dag, name='files workflow', fileset=fileset)

# run the workflow
wf.run()

# check the status of the workflow
print('The workflow finished with state:')
print(wf.state)

# print the output of task 1
print('Downloaded files:\n', wf.outputs.get('downloaded_files'))