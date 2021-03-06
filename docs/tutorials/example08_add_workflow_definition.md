This example introduces the following NEW concepts:

- Create WorkflowDefinition

- For WorkflowDefinition:

    - use *inputsschema* to specify the allowed parameters in main DAG

    - use *filesschema* to specify the allowed files in main DAG

    - use *description* to describe the workflow definition
    
    - use *account* to manage your workflow definitions
    
    - add the workflow definition to a specific project

```python
from pytailor import PythonTask, DAG, WorkflowDefinition, Account, Project, \
    InputsSchema, FilesSchema, Description, Files, Outputs, Inputs, Workflow, \
    FileSet

import glob
import shutil

# a modified dag description with parametrization from example 5

files = Files()
outputs = Outputs()
inputs = Inputs()

with DAG(name="dag") as dag:

    t1 = PythonTask(
        function=glob.glob,
        name="task 1",
        args=["**/*.txt"],
        kwargs={"recursive": True},
        download=files.testfiles,  # refers to a file tag
        output_to=outputs.downloaded_files,  # put function's return value on
        # outputs.downloaded_files
    )
    t2 = PythonTask(
        function=shutil.copyfile,
        name="task 2",
        args=[files.inpfile[0], "newfile.txt"],
        download=files.inpfile,
        upload={files.outfile: "newfile.txt"},
    )
    t3 = PythonTask(
        function=print,
        name="task 3",
        args=["My input print", inputs.print],
        parents=t1,
    )

# define inputsschema
example_inputs = {'print': 'hello, world!'}
inputs_schema = InputsSchema(inputs=example_inputs)
inputs_schema.add_defaults(example_inputs)

# define filesschema
files_schema = FilesSchema()
files_schema.add_file(tag='inpfile', ext=['txt'], required=True, multiple=False)
files_schema.add_file(tag='testfiles', ext=['txt'], required=True, multiple=True)

wf_def_description = """
This workflow definition has the following steps:
    - Download testfiles and sends filename as output
    - Download inpfile and upload files
    - prints the inputs.print argument
"""
description = Description.from_dag(dag,
                                   wf_def_name='Example 8 Hello world workflow '
                                               'definition',
                                   wf_def_description=wf_def_description)


# create the workflow definition

wf_def = WorkflowDefinition(
    name=description.name,
    description=description.to_string(),
    dag=dag,
    inputs_schema=inputs_schema.to_dict(),
    files_schema=files_schema.to_dict()
)

# get an account and add wf_def to account
# (requires account admin privileges)
account = Account.get_my_accounts()[0]
wf_def.add_to_account(account)

# wf_def has now gotten an id
print(wf_def.id)

# the workflow definition can now be added to a project
# (requires account admin privileges)
prj = Project.from_name("Test")
prj.add_workflow_definition(wf_def.id)

``` 

The workflow definition is now available as a definition to create a new workflow in the 
Tailor Web APP

![List](New_workflow.png)

You can list available workflow definitions 
```python

prj.list_available_workflow_definitions()

```

The definition can be collected from project and definition id at a later stage, and a
 workflow can also be instantiated from a workflow definition id. 

```python
wf_def = WorkflowDefinition.from_project_and_id(prj, wf_def.id)


wf = Workflow.from_definition_id(project=prj,
                                 wf_def_id=wf_def.id,
                                 name="my workflow",
                                 inputs=example_inputs,
                                 fileset=fileset)
wf.run()
```

Executing a workflow from workflow definition makes it possible to start it 
from the Tailor Web App.

![List](Start_new.png)

 

You can remove your own definitions from project

```python
prj.remove_workflow_definition(wf_def.id)
```
