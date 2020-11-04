from pytailor import Workflow, Project, FilesSchema, WorkflowDefinition, Account

prj = Project.from_name("Test")
wf = Workflow.from_project_and_id(prj, 277)
files_schema = FilesSchema.from_fileset_and_dag(wf.fileset, wf.dag)
wf_def = WorkflowDefinition.from_workflow(wf, wf_def_description='test',
                                          wf_def_name='test')
account = Account.get_my_accounts()[0]
wf_def.add_to_account(account)
prj.add_workflow_definition(wf_def.id)
