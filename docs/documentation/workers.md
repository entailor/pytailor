
## Worker

A worker is a process that asks the [Tailor backend](account_management.md) for 
tasks that are ready. During runtime the worker process reports back the status 
of the task execution. Once the task is completed, the worker process is ready to 
execute a new tasks that is ready in the database.  

To start a worker, open a terminal in an environment where you have pytailor installed
and write:

```
tailor worker
```

A worker with the default configuration as defined in the _/.tailor/config.toml_ file will now start
asking for tasks to execute.

If you want to configure the worker to sleep for 5 seconds between each time it asks for work, using 
10 cores on the computer.

```
tailor worker --sleep 5 --ncores 10 
```

For a complete list of possible worker configurations write

```
tailor worker --help
```

If you want to run several different workers with different configurations, simply open 
several terminals and repeat.

## Worker management

### Filter on project

Workers may be configured to only run tasks in a workflow that belongs to a specific 
[project](account_management.md). This is done by assigning a project at initiation:

```shell
tailor worker --project-id-filter <your_project_id_filter (project.id)>
```

Multiple projects may be assigned by repeating the configuration key:

```shell
tailor worker --project-id-filter <id_1> --project-id-filter <id_2>
```

### Filter on worker name

A workflow may be distributed to run only on workers with a given worker name. 
To run these workflows, the same worker name must be specified. 
 
```
tailor worker --workername <my_worker_name (string)>
```

#### Example

Workflow execution
```python
from pytailor import PythonTask, DAG, Project, Workflow

with DAG(name="dag") as dag:
    t1 = PythonTask(
        function="builtins.print",
        name="job 1",
        args=["Hello, world!"],
    )
# open a project
prj = Project.from_name("Test")

### workflow execution ###

# create a workflow
wf = Workflow(
    project=prj,
    dag=dag,
    name="Hello from pytailor",
)

wf.run(distributed=True, workername='my_worker')

```

Configuring worker
```shell
tailor worker --workername my_worker
```


### Filter on task requirement

Tasks may *require* a certain *capability* for the worker environment, such as installed software. 
To tag a worker with the requirement, *capability* is applied at worker configuration. 
 
```
tailor worker --capability <specified_capability_requirement_in_task (string)>
```

#### Example

Task definition
```python
from pytailor import PythonTask

t1 = PythonTask(
    function='builtins.print',
    name='capability demo',
    args=['hello capability!'],
    requirements=['key1']
)
```

Configuring worker
```shell
tailor worker --capability key1
```

Multiple capabilities may be assigned by repeating the configuration key:

```shell
tailor worker --capability key1 --capability key2
```