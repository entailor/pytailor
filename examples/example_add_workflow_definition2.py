from pytailor import PythonTask, DAG, Account, WorkflowDefinition, Project


# a simple dag definition

with DAG(name="dag") as dag:

    t1 = PythonTask(
        function="time.sleep", name="task 1", args=["<% $.inputs.sleep_time %>"]
    )
    t2 = PythonTask(
        function="builtins.print",
        name="task 2",
        args=["\nSlept for", "<% $.inputs.sleep_time %>", "second"],
        kwargs={"sep": "   ", "end": "\n\n"},
        parents=t1,
    )

# inputs schema
inputs_schema = {
    "title": "Inputs",
    "description": "Inputs for the Workflow",
    "outputs": {},
    "type": "object",
    "inputs": {
        "$schema": "http://json-schema.org/schema#",
        "type": "object",
        "properties": {"sleep_time": {"type": "number"}},
        "required": ["sleep_time"],
    },
}

# files schema
files_schema = {
    "in": {
        "coordfile": {
            "ext": ["txt"],
            "title": "Coordinates",
            "description": "A file with coordinate values of nodes",
            "required": True,
        },
        "test": {
            "ext": ["pdf"],
            "multiple": True,
            "title": "Test",
            "description": "Just a test",
        },
    }
}

# create the workflow definition

wf_def = WorkflowDefinition(
    name="Hello world workflow definition",
    description="""
    # A markdown description string
    
    This is the hello world workflow definition in tailor.
    """,
    dag=dag,
    inputs_schema=inputs_schema,
    files_schema=files_schema,
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
