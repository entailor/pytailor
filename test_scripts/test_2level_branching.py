"""
This script defines and executes a 2-level branching workflow and makes assertions for
the expected inputs, outputs and files at different scoping levels
"""

from pytailor import PythonTask, BranchTask, DAG, Workflow, Project, FileSet

### DAG with two levels of branching ###

with DAG(name="DAG") as dag_2lvl_dup:
    # root task of outer dag
    t1 = PythonTask(
        name="T1", function=dict, kwargs={"0": 3, "1": 4, "2": 5},
        output_to="out_from_T1"
    )

    # outer branching
    with BranchTask(
            name="DUP1",
            parents=t1,
            branch_data=["<% $.files.testfiles1 %>", "<% $.inputs.data %>"],
            branch_files=["testfiles1"],
    ) as dup1:
        # sub-dag to duplicate
        with DAG(name="SUBDAG") as sub_dag:
            t2 = PythonTask(
                name="T2",
                function="shutil.copyfile",
                args=["<% $.files.testfiles1[0] %>", "newfile1.txt"],
                download="testfiles1",
                upload={"copied_files1": "newfile1.txt"},
                output_to="out_from_T2",
            )

            # inner branching
            with BranchTask(
                    name="DUP2",
                    parents=t2,
                    branch_data=[
                        "<% $.files.testfiles2 %>",
                        "<% $.outputs.out_from_T1 %>",
                        "<% $.inputs.data %>",
                    ],
                    branch_files=["testfiles2"],
            ) as dup2:
                with DAG(name="SUBSUBDAG"):
                    t3 = PythonTask(
                        name="T3",
                        function="shutil.copyfile",
                        args=["<% $.files.testfiles2[0] %>", "newfile2.txt"],
                        download="testfiles2",
                        upload={"copied_files2": "newfile2.txt"},
                        output_to="out_from_T3",
                    )

                    PythonTask(
                        name="T4",
                        function="builtins.str",
                        args=["<% $.outputs.out_from_T1 %>"],
                        output_to="out_from_T4",
                        parents=t3,
                    )
                    PythonTask(
                        name="T5",
                        function="builtins.str",
                        args=["<% $.inputs.data %>"],
                        output_to="out_from_T5",
                        parents=t3,
                    )

            # last task in sub-dag
            PythonTask(
                name="T6",
                function="builtins.str",
                args=["<% $.inputs.data %>"],
                output_to="out_from_T6",
                parents=dup2,
            )

            PythonTask(
                name="T7",
                function=dict,
                args=["<% $.outputs.out_from_T3 %>"],
                output_to="out_from_T7",
                parents=dup2,
            )

            PythonTask(
                name="T8",
                function=str,
                args=["<% $.outputs.out_from_T2 %>"],
                output_to="out_from_T8",
                parents=dup2,
            )

    PythonTask(
        name="T9",
        function=dict,
        args=["<% $.outputs.out_from_T3 %>"],
        output_to="out_from_T9",
        parents=dup1,
    )

    PythonTask(
        name="T10",
        function=dict,
        args=["<% $.outputs.out_from_T2 %>"],
        output_to="out_from_T10",
        parents=dup1,
    )

### Workflow ###

# open a project
prj = Project.from_name("Test")

# create a fileset and upload files
fileset = FileSet(prj)
fileset.upload(
    testfiles1=[
        "testfiles/testfile_01.txt",
        "testfiles/testfile_02.txt",
        "testfiles/testfile_03.txt",
    ],
    testfiles2=[
        "testfiles/testfile_01.txt",
        "testfiles/testfile_02.txt",
        "testfiles/testfile_03.txt",
    ],
)

# inputs
inputs = {"data": [[0, 1, 2], ["a", "b", "c"], [6, 7, 8]]}

# create a workflow
wf = Workflow(
    project=prj,
    dag=dag_2lvl_dup,
    name="2-level brancing test",
    fileset=fileset,
    inputs=inputs,
)

target_outputs = {'out_from_T1': {'0': 3, '1': 4, '2': 5},
                  'out_from_T10': {'0': 'newfile1.txt',
                                   '1': 'newfile1.txt',
                                   '2': 'newfile1.txt'},
                  'out_from_T2': {'0': 'newfile1.txt', '1': 'newfile1.txt',
                                  '2': 'newfile1.txt'},
                  'out_from_T3': {'0': {'0': 'newfile2.txt',
                                        '1': 'newfile2.txt',
                                        '2': 'newfile2.txt'},
                                  '1': {'0': 'newfile2.txt',
                                        '1': 'newfile2.txt',
                                        '2': 'newfile2.txt'},
                                  '2': {'0': 'newfile2.txt',
                                        '1': 'newfile2.txt',
                                        '2': 'newfile2.txt'}},
                  'out_from_T4': {'0': {'0': '3', '1': '4', '2': '5'},
                                  '1': {'0': '3', '1': '4', '2': '5'},
                                  '2': {'0': '3', '1': '4', '2': '5'}},
                  'out_from_T5': {'0': {'0': '0', '1': '1', '2': '2'},
                                  '1': {'0': 'a', '1': 'b', '2': 'c'},
                                  '2': {'0': '6', '1': '7', '2': '8'}},
                  'out_from_T6': {'0': '[0, 1, 2]', '1': "['a', 'b', 'c']",
                                  '2': '[6, 7, 8]'},
                  'out_from_T7': {'0': {'0': 'newfile2.txt',
                                        '1': 'newfile2.txt',
                                        '2': 'newfile2.txt'},
                                  '1': {'0': 'newfile2.txt',
                                        '1': 'newfile2.txt',
                                        '2': 'newfile2.txt'},
                                  '2': {'0': 'newfile2.txt',
                                        '1': 'newfile2.txt',
                                        '2': 'newfile2.txt'}},
                  'out_from_T8': {'0': 'newfile1.txt', '1': 'newfile1.txt',
                                  '2': 'newfile1.txt'},
                  'out_from_T9': {'0': {'0': 'newfile2.txt',
                                        '1': 'newfile2.txt',
                                        '2': 'newfile2.txt'},
                                  '1': {'0': 'newfile2.txt',
                                        '1': 'newfile2.txt',
                                        '2': 'newfile2.txt'},
                                  '2': {'0': 'newfile2.txt',
                                        '1': 'newfile2.txt',
                                        '2': 'newfile2.txt'}}}

# assert wf.outputs == target_outputs

if __name__ == "__main__":
    wf.run(distributed=True, worker_name="test_worker")
