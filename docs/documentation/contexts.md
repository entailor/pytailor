# Contexts
Contexts represents the data and files associated with a workflow. The context consist of three datastructures:

*  **inputs**
*  **outputs**
*  **files**

_inputs_ are provided by the user during workflow specification, e.g.

``` python
from tailor import PythonTask, WorkflowSpec

# a task definition
t1 = Pythontask(
    function='builtins.abs',
    args='<% $.inputs.input_number %>'
)
t2 = Pythontask(
    function='builtins.abs',
    args='<% $.inputs.input_number %>'
)

inputs = {
    input_number: -123
}

wf_spec = WorkflowSpec(

)

```

!!! note
    The _inputs_ and _outputs_ datastructures must be JSON-serializable, which limits the data [types](https://www.geeksforgeeks.org/json-data-types/) which can be used. In the future more sophisticated serialization may be applied to allow other object types, e.g. numpy arrays. For data that is not JSON-compatible you can serialize the data to file and use the file-piping mechanisms to send the data to your tasks.

## Context queries

Contexts can be queried using the YAQL query language. _Context queries_ can be used in task definitions as a means to parameterize inputs. When jobs are executed, the queries are performed on the context associated with the current workflow run. Context queries, when used in task definitions, are specified using a special syntax: `'<% query-expression %>'`. This syntax tells tailor to 


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
