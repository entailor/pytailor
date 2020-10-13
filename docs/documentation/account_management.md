# Tailor Backend

The data, files, tasks, workflows and workers are orchestrated by the tailor backend. 
A config file with a valid user api key must exist, to let the pytailor client 
communicate with the backend. 

## User accounts

You can request a free user account at [tailor.wf](https://tailor.wf). The user account
lets you access web app, with an overview of your projects, workflows and workflow definitions. 

## Projects

A workflow must belong to a Project, where the workflow, including tasks, files and data
is stored. 

For the basic user registration two default projects are created for you:
 
 - Project *Test* is your private project, set up to let you experiment on your own
 - Project *Prod* is set up to allow users on the same account to collaborate. 
 
[Workers](workers.md) may also be set up to only run 
tasks that belong to a specific project.  

## Accounts

To share your defined workflow ([workflow definition](../api/workflow_definition.md)) 
with other users in your team, a workflow definition must be added to your Account. 
The account is shared between the different users in your organization or workgroup.

Your colleagues in your account may also start a new workflow from your workflow 
definitions.


## Workflow definition subscriptions

You may run workflows based on definitions from other accounts. This is done by adding 
the *id* of the other account's workflow definition to your account's *workflow 
definition subscription list*. 

Vise verca you may allow others to *subscribe* to your workflow definitions. 

In both cases the workflows are run on the workers belonging to the creator, such that
the code is not exposed to the subscriber.

