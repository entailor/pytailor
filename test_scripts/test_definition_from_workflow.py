from pytailor import Workflow, Project, FilesSchema, WorkflowDefinition, Account

# first run a workflow to use as basis
from test_minimal import dag
prj = Project.from_name("Test")
wf = Workflow(project=prj, dag=dag, name="minimal workflow")
wf.run()
assert wf.state == "COMPLETED"

# reload workflow from backend
wf = Workflow.from_project_and_id(prj, wf.id)
files_schema = FilesSchema.from_fileset_and_dag(wf.fileset, wf.dag)
wf_def = WorkflowDefinition.from_workflow(wf, wf_def_description='test',
                                          wf_def_name='test')
account = Account.get_my_accounts()[0]
wf_def.add_to_account(account)
prj.add_workflow_definition(wf_def.id)

# cleanup
prj.remove_workflow_definition(wf_def.id)
prj.delete_workflow(wf.id)
