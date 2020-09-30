"""
pyTailor Example 6

This example introduces the following NEW concepts:
    - Use BranchTask to "branch out" a single PythonTask
    - For BranchTask definitions:
        - Use *branch_data* to specify which data to use for branching

*branch_data* is given as one or more query-expressions. When branching is performed
the query-expressions must evaluate to to a list or a dict. If the queries evaluates to a
dict, that dict must have integer keys to represent the index of each branch.

Branched tasks always become children of the BranchTask that created them.

"""

from pytailor import PythonTask, BranchTask, DAG, Workflow, Project, Inputs

### workflow definition ###

inputs = Inputs()

with DAG(name="dag") as dag:
    with BranchTask(name="duplicate", branch_data=[inputs.data]):
        PythonTask(
            function=print,
            name="task 1",
            args=[inputs.data, inputs.other],
        )

### workflow run ###

# open a project
prj = Project.from_name("Test")

wf_inputs = {
    "data": [1, 2],
    # 'data': {0: 1, 1: 2},  # alternatively use a dict with int keys
    "other": "this is not used for branching",
}

# create a workflow:
wf = Workflow(project=prj, dag=dag, name="branch workflow", inputs=wf_inputs)

# run the workflow
wf.run()

# check the status of the workflow
print("The workflow finished with state:")
print(wf.state)
