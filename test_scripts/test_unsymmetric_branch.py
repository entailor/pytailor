from pytailor import PythonTask, BranchTask, DAG, Workflow, Project, Inputs, Outputs

inputs = Inputs()
outputs = Outputs()

with DAG(name="dag") as dag:
    with BranchTask(branch_data=inputs.panels,
                    name='branch on panels') as panel_branch:
        with BranchTask(branch_data=inputs.panels.SN_curves,
                        name='branch on s/n-curves') as sn_curve_branch:
            with DAG(name="sub-dag"):
                t1 = PythonTask(
                    function=str,
                    name="task 1",
                    args=[inputs.panels.id],
                    output_to=outputs.out1
                )
                PythonTask(
                    function=str,
                    name="task 2",
                    args=[inputs.panels.SN_curves],
                    output_to=outputs.out2,
                    parents=t1
                )

workflow_inputs = {
    'panels': [
        {'id': 'panel1', 'SN_curves': [1, 2, 3]},
        {'id': 'panel2', 'SN_curves': [1, 2]},
        {'id': 'panel3', 'SN_curves': [1, 2, 3, 4]}
    ]
}

### run workflow ###

# open a project
prj = Project.from_name("Test")

# create a workflow:
wf = Workflow(project=prj, dag=dag, name="inputs workflow", inputs=workflow_inputs)

target_outputs = {
    'out1': {'0': {'0': 'panel1', '1': 'panel1', '2': 'panel1'},
             '1': {'0': 'panel2', '1': 'panel2'},
             '2': {'0': 'panel3', '1': 'panel3', '2': 'panel3', '3': 'panel3'}},
    'out2': {'0': {'0': '1', '1': '2', '2': '3'},
             '1': {'0': '1', '1': '2'},
             '2': {'0': '1', '1': '2', '2': '3', '3': '4'}}}
