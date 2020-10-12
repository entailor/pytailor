# Workers

## Worker

A worker is a process that asks for tasks that are ready in the Tailor database. 
During runtime the worker process reports back the status of the task execution. Once the task is completed, 
the worker process is ready to execute a new tasks that is ready in the database.


To start a worker, open a terminal in the pytailor environment and write

```
tailor worker
```

A worker with the default configuration as defined in the _/.tailor/config.toml_ file will now start
asking for tasks to execute.

If you want to configure the worker to sleep for 5 seconds between each time it asks for work, using 
10 cores on the computer and executing workflows with the specified worker name _my_worker_name_, 
write:

```
tailor worker --sleep 5 --n_cores 10 --worker_name my_worker_name
```

For a complete list of possible worker configurations write

```
tailor worker --help
```

If you want to run several different workers with different configurations, simply open 
several terminals and repeat