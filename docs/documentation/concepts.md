# Tailor concepts

## DAGs

DAGs are used to define relationships between tasks in a Workflow in the form of a
Directed Acyclic Graph.

## Task definitions

Task _definitions_ are parameterized and reusable blueprints for computing tasks.

In Pytailor, tasks definitions are created using the
[task definition classes](../api/taskdefs.md)

The available task definition classes are:

- **PythonTask**
    This is the basic building block. Used to define the execution of a
    single Python function (callable).
- **BranchTask**
    ...

By combining the different task types, arbitrary complex tasks can be defined.
A non-trivial task definition will typically consist of a DAG at the top-level,
which in turn consist of other task definitions as illustrated in ...

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

## Workflow subscriptions

Workflow definitions can be shared between users with Workflow _subscriptions_.

## Tailor Accounts


## Tailor Projects


