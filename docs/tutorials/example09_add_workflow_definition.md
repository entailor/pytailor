This example introduces nested inputs as an example of how a complex input schema 
is rendered in the web interface

```python

from pytailor import PythonTask, BranchTask, DAG, WorkflowDefinition, Account, \
    Project, InputsSchema, Description, Inputs

import builtins

# a modified dag description with parametrization from example 5

inputs = Inputs()

with DAG(name="dag") as dag:
    with BranchTask(branch_data=inputs.panels, name='branch on panels') as panel_branch:
        with BranchTask(branch_data=inputs.panels.SN_curves, name='branch on s/n-curves') as sn_curve_branch:
            t1 = PythonTask(
                function=builtins.print,
                name="task 1",
                args=[inputs.panels.id, inputs.panels.SN_curves]
            )

inputs = {'panels': [
    {'id': 'panel1', 'SN_curves': [1, 2, 3]},
    {'id': 'panel2', 'SN_curves': [1, 2]},
    {'id': 'panel3', 'SN_curves': [1, 2, 3, 4]}]}


# define inputsschema
inputs_schema = InputsSchema(inputs=inputs)
inputs_schema.add_defaults(inputs)


wf_def_description = """
This workflow definition has the following steps:
    
    - prints the inputs.print argument
"""
description = Description.from_dag(dag,
                                   wf_def_name='Example 9 Two level branch workflow '
                                               'definition',
                                   wf_def_description=wf_def_description)


# create the workflow definition

wf_def = WorkflowDefinition(
    name=description.name,
    description=description.to_string(),
    dag=dag,
    inputs_schema=inputs_schema.to_dict(),
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