
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
tailor worker --sleep 5 --n_cores 10 
```

For a complete list of possible worker configurations write

```
tailor worker --help
```

If you want to run several different workers with different configurations, simply open 
several terminals and repeat

## Filter on project

Workers may be configured to only run tasks in a workflow that belong to a specific 
[project](account_management.md). This is done by assigning a project at initiation:

```shell
tailor worker --project_id_filter <your_project_id_filter>
```
    

## Worker name

At initiation of workflows, a workflow may be distributed to run only on workers with
 a given worker name. To run these workflows, the same worker name must be specified. 
 
```
tailor worker --worker_name my_worker_name
```



## Capability

Workers may be configured such that the tasks that *requires*
 a certain *capability* is run on the worker. This is done by assigning capabilities
 to the worker  at initiation:
 
```
tailor worker --capability <specified_capability_requirement_in_task>
```

