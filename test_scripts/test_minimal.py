from pytailor import PythonTask, DAG, Workflow, Project

### workflow definition ###

with DAG(name="dag") as dag:
    PythonTask(
        function="builtins.print",
        name="task 1",
        args=["OK"],
    )


if __name__ == "__main__":
    ### workflow run ###

    # open a project
    prj = Project.from_name("Test")

    # create a workflow:
    wf = Workflow(project=prj, dag=dag, name="minimal workflow")

    # run the workflow
    wf.run()

    # check the status of the workflow
    print("The workflow finished with state:")
    print(wf.state)

    assert wf.state == "COMPLETED"

    # cleanup
    prj.delete_workflow(wf.id)
