### pyTailor Example 3
This example introduces the following NEW concepts:

- For task definitions:

    - Using query expressions.

- Specifying *inputs* when creating a workflow

Query expressions is a means to parameterize the inputs that are specified in
a task definition. The query will be applied later when the workflow is
executed and the parameters to use will be extracted from the input provided
to that specific workflow. To use a query, the query string must be on the
format "<% query %>". The yaql python package is used for handling queries, see
https://yaql.readthedocs.io/en/latest/index.html.

Inputs are immutable, in the sense that they cannot be changed during the execution
of the workflow.

NOTE: Currently this mechanism only work with data that is directly

-serializable. In the future non-JSON compatible objects may be handled
as well (by use of pickling).

``` python 
from pytailor import PythonTask, DAG, Workflow, Project

### workflow definition ###

with DAG(name="dag") as dag:

    t1 = PythonTask(
        function="time.sleep", name="task 1", args=["<% $.inputs.sleep_time %>"]
    )
    t2 = PythonTask(
        function="builtins.print",
        name="task 2",
        args=["\nSlept for", "<% $.inputs.sleep_time %>", "second"],
        kwargs={"sep": "   ", "end": "\n\n"},
        parents=t1,
    )

### run workflow ###

# open a project
prj = Project.from_name("Test")

# define inputs
inputs = {"sleep_time": 1.5}  # try to change this and rerun the workflow

# create a workflow:
wf = Workflow(project=prj, dag=dag, name="inputs workflow", inputs=inputs)

# run the workflow
wf.run()

# check the status of the workflow
print("The workflow finished with state:")
print(wf.state)

# inputs are available on the run object
print("Inputs were:")
print(wf.inputs)
```