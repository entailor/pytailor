# -*- coding: utf-8 -*-
"""
pyTailor Example 11

"""

from pytailor import PythonTask, DAG, Workflow, Project

### workflow definition ###


# use an "inline" function, workflow cannot be run in distributed mode.
def print_kwargs(*args, **kwargs):
    print(args)
    print(kwargs)


config = {
    "default1": [1, 2, 3],
    "a": {
        "asdf": "<% inputs.asdf %>"
    }
}

args = [1, 2, config]


with DAG(name="dag") as dag:

    t1 = PythonTask(
        function=print_kwargs,
        name="task 1",
        args=args,
        kwargs=config,
    )

### run workflow ###

inputs = {
    "asdf": 123
}

# open a project
prj = Project.from_name("Test")

# create a workflow:
wf = Workflow(project=prj, dag=dag, name="nested query workflow", inputs=inputs)

# run the workflow
wf.run()
