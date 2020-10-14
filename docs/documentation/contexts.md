# Contexts
Contexts represents the data and files associated with a workflow. 
The context consist of three data structures:

*  **inputs**
*  **outputs**
*  **files**

_inputs_ are provided by the user during workflow creation, e.g.

```python
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

```

!!! note
    The _inputs_ and _outputs_ data structures must be JSON-serializable, 
    which limits the data [types](https://www.geeksforgeeks.org/json-data-types/) which can be used. 
    In the future more sophisticated serialization may be applied to allow other 
    object types, e.g. numpy arrays. For data that is not JSON-compatible you can 
    serialize the data to file and use the file-piping mechanisms to send the data to your tasks.


## Fileset
A fileset represents an isolated file storage area in the Tailor backend and is 
associated with a specific workflow run.

<!---
## Scoped contexts
Scoped contexts arise when tasks are duplicated.

Consider the following DAG, consisting of two PythonTasks:
``` python
              +---+
              |t1 |  PythonTask(..., output_to='out')
              +-+-+
                |
                |
              +-v-+
              |t2 |  PythonTask(..., args='<% $.outputs.out %>')
              +---+
```
When this DAG is duplicated with a BranchTask
-->