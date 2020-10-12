# Programming workflows

## DAGs

DAGs are used to define relationships between tasks in a Workflow in the form of a
Directed Acyclic Graph. 

That the DAG is "Directed" means that the parent task is 
computed before the child task. 

That the DAG is "Acyclic" means that there is no way to start at any task _t_ and follow a consistently-directed 
sequence of tasks that eventually loops back to _t_ again. In other words there are no loops in 
the workflow. This means that strictly speaking an iteration loop (while loop) is not allowed in
a Tailor workflow. Since iteration loops are a necessary part of many engineering workflows, 
we are currently developing a WhileTask. A WhileTask has an internal loop that runs until a condition is met. 
The child of the WhileTask only "sees" the resulting output and thus the WhileTask behaves just as 
any other task in the workflow.

## Task definitions

Task _definitions_ are parameterized and reusable blueprints for computing tasks.

In Pytailor, tasks definitions are created using the
[task definition classes](../api/taskdefs.md)

The available task definition classes are:

- **PythonTask**
    
    This is the basic building block, used to define the execution of a
    single Python function (callable).
    
- **BranchTask**
    
    This is the basic branching building block. It creates branches based on files or data. 

- **WhileTask** (in development)
    
    This is the basic iteration building block. It runs the same task over and over with updated input data until a 
    condition is met. 


By combining the different task types, arbitrary complex tasks can be defined.
A non-trivial task definition will typically consist of a DAG at the top-level,
which in turn consist of other task definitions as illustrated in tutorials 
[6](../tutorials/example06_branch_task.md), [7](../tutorials/example07_branch_dag.md) 
and [9](../tutorials/example09_add_workflow_definition.md).

???+ note
    Tailor is still in development and more task definition classes are likely to be
    introduced in the future to extend functionality.


## Workflows

Workflows are instantiated DAGs with a given set of inputs and files.  Workflows are
stored on the Tailor backend under a given [Project](#tailor-projects).

- dag
- project
- inputs (parameters, JSON)
- files (inputs files)
- worker requirements

In Pytailor, workflows are represented by the [Workflow]() class

## Tasks
Tasks are instantiated _task definitions_. Belongs to a _Workflow_.

## Workflow definitions

Workflow _definitions_ are used to store a DAG along with requirements (schema) for inputs
and files. Workflow definitions are stored in the backend and can be made available for
other users. 
