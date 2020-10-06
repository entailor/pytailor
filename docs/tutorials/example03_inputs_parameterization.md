### pyTailor Example 3
``` python 
from pytailor import PythonTask, DAG, Workflow, Project, Inputs

import time

### workflow definition ###


inputs = Inputs()

with DAG(name="dag") as dag:

    t1 = PythonTask(
        function=time.sleep, name="task 1", args=[inputs.data.sleep_time[0]]
    )
    t2 = PythonTask(
        function=print,
        name="task 2",
        args=["\nSlept for", inputs.data, "second"],
        kwargs={"sep": inputs.sep, "end": "\n\n"},
        parents=t1,
    )

### run workflow ###

# open a project
prj = Project.from_name("Test")

# define inputs
wf_inputs = {"data": {"sleep_time": [1.5]},
             "sep": "   "}

# create a workflow:
wf = Workflow(project=prj, dag=dag, name="inputs workflow", inputs=wf_inputs)

# run the workflow
wf.run()

# check the status of the workflow
print("The workflow finished with state:")
print(wf.state)

# inputs are available on the run object
print("Inputs were:")
print(wf.inputs)
```