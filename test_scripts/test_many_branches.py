import time

from pytailor import PythonTask, BranchTask, DAG, Workflow, Project

### workflow definition ###

with DAG(name="dag") as dag:
    with BranchTask(name="duplicate1",
                    branch_data=["<% $.inputs.data1 %>"]) as branch1:
        with DAG(name="sub-dag"):
            with BranchTask(name="duplicate2",
                            branch_data=["<% $.inputs.data2 %>"]) as branch2:
                with DAG(name="subsub-dag"):
                    with BranchTask(
                            name="duplicate3",
                            branch_data=["<% $.inputs.data3 %>"]) as branch3:
                        PythonTask(
                            function=time.sleep,
                            name="task 1",
                            args=[3.],
                        )
                    PythonTask(
                        function=print,
                        name="task 2",
                        args=["Task 2"],
                        parents=branch3
                    )
            PythonTask(
                function=print,
                name="task 3",
                args=["Task 3"],
                parents=branch2
            )
    PythonTask(
        function=print,
        name="task 4",
        args=["Task 4"],
        parents=branch1
    )



### workflow run ###

# open a project
prj = Project.from_name("Test")

inputs = {
    "data1": list(range(5)),
    "data2": list(range(10)),
    "data3": [11, 22],
    "other": "this is not used for branching",
}

# create a workflow:
wf = Workflow(project=prj, dag=dag, name="branch workflow", inputs=inputs)


if __name__ == "__main__":
    wf.run(distributed=True, worker_name="test_worker")
