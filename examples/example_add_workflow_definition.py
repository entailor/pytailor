from pytailor import PythonTask, DAG, Account, WorkflowDefinition, Project


# a simple dag definition

t1 = PythonTask(
    function="builtins.print",
    name="job 1",
    args=["\nHello, world!\n"],
)
t2 = PythonTask(
    function="builtins.print",
    name="job 2",
    args=["\nHello again,", "world!\n"],
    parents=t1,
)

dag = DAG(tasks=[t1, t2], name="dag")

# create the workflow definition

wf_def = WorkflowDefinition(
    name="Hello world workflow definition",
    description="""
    # A markdown description string
    
    This is the hello world workflow definition in tailor.
    """,
    dag=dag,
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
