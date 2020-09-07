from tailor import PythonTask, DAG, Account, WorkflowDefinition


# a simple dag definition

t1 = PythonTask(
    function='builtins.print',
    name='job 1',
    args='\nHello, world!\n',
)
t2 = PythonTask(
    function='builtins.print',
    name='job 2',
    args=['\nHello again,', 'world!\n'],
    parents=t1
)

dag = DAG(tasks=[t1, t2], name='dag')

# create the workflow definition

wf_def = WorkflowDefinition(
    name='Hello world workflow definition',
    description="""
    # A markdown description string
    
    This is the hello world workflow definition in tailor.
    """,
    dag=dag
)

# get an account and add wf_def to account

account = Account.get_my_accounts()[0]
wf_def.add_to_account(account)

# reload the account and assert that the workflow definition was added
account = Account.get_my_accounts()[0]
assert wf_def.id in account.workflow_definitions_owned
