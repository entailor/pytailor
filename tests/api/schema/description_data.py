
wf_def_description = """
        pyTailor Example 7
        
        This example introduces the following NEW concepts:
            - Use BranchTask to "branch out" a DAG
            - For BranchTask definitions:
                - Use *branch_files* to specify which files to use for branching
        
        *branch_files* is given as one or more file tags.
        """

from pytailor import PythonTask, BranchTask, DAG

### workflow definition ###

with DAG(name="duplicate dag example") as dag:
    with BranchTask(
        name="branch",
        branch_data=["<% $.files.testfiles %>"],
        branch_files=["testfiles"],
    ):
        with DAG(name="sub-dag") as sub_dag:
            t1 = PythonTask(
                function="glob.glob",
                name="task 2",
                args=["**/*.txt"],
                kwargs={"recursive": True},
                download="testfiles",
                output_to="glob_res",
            )
            PythonTask(
                function="builtins.print",
                name="task 3",
                args=["<% $.files.testfiles %>", "<% $.outputs.glob_res %>"],
                parents=t1,
            )

wf_def_name = 'duplicate dag example'
