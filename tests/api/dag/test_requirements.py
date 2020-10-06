from pytailor import PythonTask, BranchTask, DAG, Inputs


def test_specify_requirements_at_dag_level():
    inputs = Inputs()
    with DAG(requirements=["asdf", "fdsa"]) as dag:
        t1 = PythonTask(function=print,
                        args=["test t1"])
        with BranchTask(branch_data=inputs.data, parents=t1) as branch:
            with DAG() as sub_dag:
                t2 = PythonTask(function=print,
                                args=["test t2"])
                t3 = PythonTask(function=print,
                                args=["test t3"],
                                parents=t2)

    target1 = ["pytailor"]
    target2 = ["asdf", "fdsa", "pytailor"]
    assert dag.requirements == target2
    assert t1.requirements == target2
    assert branch.requirements == target2
    assert sub_dag.requirements == target2
    assert t2.requirements == target2
    assert t3.requirements == target2

    assert dag.get_all_requirements() == target2
    assert t1.get_all_requirements() == target2
    assert branch.get_all_requirements() == target2
    assert sub_dag.get_all_requirements() == target2
    assert t2.get_all_requirements() == target2
    assert t3.get_all_requirements() == target2


def test_specify_requirements_at_branch_level():
    inputs = Inputs()
    with DAG() as dag:
        t1 = PythonTask(function=print,
                        args=["test t1"])
        with BranchTask(branch_data=inputs.data, parents=t1,
                        requirements=["asdf", "fdsa"]) as branch:
            with DAG() as sub_dag:
                t2 = PythonTask(function=print,
                                args=["test t2"])
                t3 = PythonTask(function=print,
                                args=["test t3"],
                                parents=t2)

    target1 = ["pytailor"]
    target2 = ["asdf", "fdsa", "pytailor"]
    assert dag.requirements == target1
    assert t1.requirements == target1
    assert branch.requirements == target2
    assert sub_dag.requirements == target2
    assert t2.requirements == target2
    assert t3.requirements == target2

    assert dag.get_all_requirements() == target2
    assert t1.get_all_requirements() == target1
    assert branch.get_all_requirements() == target2
    assert sub_dag.get_all_requirements() == target2
    assert t2.get_all_requirements() == target2
    assert t3.get_all_requirements() == target2


def test_specify_requirements_at_sub_dag_level():
    inputs = Inputs()
    with DAG() as dag:
        t1 = PythonTask(function=print,
                        args=["test t1"])
        with BranchTask(branch_data=inputs.data, parents=t1) as branch:
            with DAG(requirements=["asdf", "fdsa"]) as sub_dag:
                t2 = PythonTask(function=print,
                                args=["test t2"])
                t3 = PythonTask(function=print,
                                args=["test t3"],
                                parents=t2)

    target1 = ["pytailor"]
    target2 = ["asdf", "fdsa", "pytailor"]
    assert dag.requirements == target1
    assert t1.requirements == target1
    assert branch.requirements == target1
    assert sub_dag.requirements == target2
    assert t2.requirements == target2
    assert t3.requirements == target2

    assert dag.get_all_requirements() == target2
    assert t1.get_all_requirements() == target1
    assert branch.get_all_requirements() == target2
    assert sub_dag.get_all_requirements() == target2
    assert t2.get_all_requirements() == target2
    assert t3.get_all_requirements() == target2


def test_specify_requirements_at_task_level_1():
    inputs = Inputs()
    with DAG() as dag:
        t1 = PythonTask(function=print,
                        args=["test t1"],
                        requirements=["asdf", "fdsa"])
        with BranchTask(branch_data=inputs.data, parents=t1) as branch:
            with DAG() as sub_dag:
                t2 = PythonTask(function=print,
                                args=["test t2"])
                t3 = PythonTask(function=print,
                                args=["test t3"],
                                parents=t2)

    target1 = ["pytailor"]
    target2 = ["asdf", "fdsa", "pytailor"]
    assert dag.requirements == target1
    assert t1.requirements == target2
    assert branch.requirements == target1
    assert sub_dag.requirements == target1
    assert t2.requirements == target1
    assert t3.requirements == target1

    assert dag.get_all_requirements() == target2
    assert t1.get_all_requirements() == target2
    assert branch.get_all_requirements() == target1
    assert sub_dag.get_all_requirements() == target1
    assert t2.get_all_requirements() == target1
    assert t3.get_all_requirements() == target1


def test_specify_requirements_at_task_level_2():
    inputs = Inputs()
    with DAG() as dag:
        t1 = PythonTask(function=print,
                        args=["test t1"])
        with BranchTask(branch_data=inputs.data, parents=t1) as branch:
            with DAG() as sub_dag:
                t2 = PythonTask(function=print,
                                args=["test t2"],
                                requirements=["asdf", "fdsa"])
                t3 = PythonTask(function=print,
                                args=["test t3"],
                                parents=t2)

    target1 = ["pytailor"]
    target2 = ["asdf", "fdsa", "pytailor"]
    assert dag.requirements == target1
    assert t1.requirements == target1
    assert branch.requirements == target1
    assert sub_dag.requirements == target1
    assert t2.requirements == target2
    assert t3.requirements == target1

    assert dag.get_all_requirements() == target2
    assert t1.get_all_requirements() == target1
    assert branch.get_all_requirements() == target2
    assert sub_dag.get_all_requirements() == target2
    assert t2.get_all_requirements() == target2
    assert t3.get_all_requirements() == target1


def test_specify_requirements_at_task_level_3():
    inputs = Inputs()
    with DAG() as dag:
        t1 = PythonTask(function=print,
                        args=["test t1"])
        with BranchTask(branch_data=inputs.data, parents=t1) as branch:
            with DAG() as sub_dag:
                t2 = PythonTask(function=print,
                                args=["test t2"])
                t3 = PythonTask(function=print,
                                args=["test t3"],
                                parents=t2,
                                requirements=["asdf", "fdsa"])

    target1 = ["pytailor"]
    target2 = ["asdf", "fdsa", "pytailor"]
    assert dag.requirements == target1
    assert t1.requirements == target1
    assert branch.requirements == target1
    assert sub_dag.requirements == target1
    assert t2.requirements == target1
    assert t3.requirements == target2

    assert dag.get_all_requirements() == target2
    assert t1.get_all_requirements() == target1
    assert branch.get_all_requirements() == target2
    assert sub_dag.get_all_requirements() == target2
    assert t2.get_all_requirements() == target1
    assert t3.get_all_requirements() == target2
