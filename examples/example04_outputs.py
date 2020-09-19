# -*- coding: utf-8 -*-
"""
pyTailor Example 4

This example introduces the following NEW concepts:
    - For PythonTask definitions:
        - Specifying what to do with function output
        - Accessing function output in downstream tasks
        - Specifying multiple parents

The *output* argument to PythonTask can be specified in two forms:
    1. A single string. Then the entire return value of the function is put on
       $.outputs.<output>.
    2. A dictionary. Then for each (tag: query) in the dict the query is
       applied to the return value and the result is put on $.outputs.<tag>

The output can be accessed in downstream tasks using query expressions like
"<%  $.outputs.<tag> %>". The output is also available as an attribute (dict)
on the workflow run objects retrieved from the database (WorkflowRun.outputs).

NOTE: Currently this mechanism only work with data that is directly
JSON-serializable. In the future non-JSON compatible objects will be handled
as well (by use of pickling).
"""

from pytailor import PythonTask, DAG, Workflow, Project

### workflow definition ###

with DAG(name='dag') as dag:

    t1 = PythonTask(
        function='glob.glob',
        name='task 1',
        args=['../*.py'],
        output_to='parentdir_content'  # form 1: single string
    )
    t2 = PythonTask(
        function='os.getcwd',
        name='task 2',
        output_extraction={'curdir': '<% $ %>'}  # form 2: (tag: query) dict
    )
    t3 = PythonTask(
        function='builtins.print',
        name='task 3',
        args=[
            'Python files in parent dir (as list):',
            '<% $.outputs.parentdir_content %>',
            'Current working dir:',
            '<% $.outputs.curdir %>'
        ],
        kwargs={'sep': '\n\n', 'end': '\n\n'},
        parents=[t1, t2]
    )

### run workflow ###

# open a project
prj = Project.from_name('Test')

# create a workflow:
wf = Workflow(project=prj, dag=dag, name='outputs workflow')

# run the workflow
wf.run()

# check the status of the workflow
print('The workflow finished with state:')
print(wf.state)

# outputs are available on the run object
print("Outputs are:")
print(wf.outputs)
