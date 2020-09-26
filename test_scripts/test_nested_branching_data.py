from pytailor import PythonTask, BranchTask, DAG, Workflow, Project

### workflow definition ###

with DAG(name="dag") as dag:
    with BranchTask(name="duplicate1", branch_data=["<% $.inputs.data1 %>"]):
        with BranchTask(name="duplicate2", branch_data=["<% $.inputs.data2 %>"]):
            with BranchTask(name="duplicate3", branch_data=["<% $.inputs.data3 %>"]):
                PythonTask(
                    function="builtins.print",
                    name="task 1",
                    args=["<% $.inputs.data1 %>", "<% $.inputs.data2 %>",
                          "<% $.inputs.data3 %>", "<% $.inputs.other %>"],
                )

### workflow run ###

# open a project
prj = Project.from_name("Test")

inputs = {
    "data1": [1, 2],
    "data2": [11, 22],
    "data3": [111, 222],
    "other": "this is not used for branching",
}

# create a workflow:
wf = Workflow(project=prj, dag=dag, name="branch workflow", inputs=inputs)

# run the workflow
wf.run()

# check the status of the workflow
print("The workflow finished with state:")
print(wf.state)
