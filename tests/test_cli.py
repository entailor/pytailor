from unittest.mock import patch
from multiprocessing import cpu_count
from pathlib import Path

from click.testing import CliRunner

from pytailor.cli.main import cli
from pytailor.utils import default_worker_name
import pytailor.config


mocked_worker_config = {
    "my_config": {
        "sleep": 1,
        "ncores": 2,
        "workername": "asdf",
        "project_ids": ["prj_id_1", "prj_id_2"],
    }
}


@patch("pytailor.cli.main.run_worker")
@patch("pytailor.cli.main.workflow_definition_compliance_test")
def test_worker_no_args(wf_def_check, run_worker):
    runner = CliRunner()
    result = runner.invoke(cli, ["worker"])

    assert result.exit_code == 0
    run_worker.assert_called_once_with(3, cpu_count() - 1, default_worker_name(), [])
    wf_def_check.assert_called_once_with([])


@patch("pytailor.cli.main.run_worker")
@patch("pytailor.cli.main.workflow_definition_compliance_test")
def test_worker_with_args(wf_def_check, run_worker):
    runner = CliRunner()
    result = runner.invoke(cli, ["worker",
                                 "--sleep", 1,
                                 "--ncores", 2,
                                 "--workername", "asdf",
                                 "--project-id-filter", "prj_id_1",
                                 "--project-id-filter", "prj_id_2"
                                 ])
    assert result.exit_code == 0
    run_worker.assert_called_once_with(1, 2, "asdf", ["prj_id_1", "prj_id_2"])
    wf_def_check.assert_called_once_with(["prj_id_1", "prj_id_2"])


@patch("pytailor.cli.main.run_worker")
@patch("pytailor.cli.main.workflow_definition_compliance_test")
def test_worker_no_checks(wf_def_check, run_worker):
    runner = CliRunner()
    result = runner.invoke(cli, ["worker",
                                 "--no-checks"
                                 ])
    assert result.exit_code == 0
    run_worker.assert_called_once_with(3, cpu_count() - 1, default_worker_name(), [])
    assert not wf_def_check.called


@patch("pytailor.cli.main.run_worker")
@patch("pytailor.cli.main.workflow_definition_compliance_test")
def test_worker_checks_only(wf_def_check, run_worker):
    runner = CliRunner()
    result = runner.invoke(cli, ["worker",
                                 "--checks-only"
                                 ])
    assert result.exit_code == 0
    wf_def_check.assert_called_once_with([])
    assert not run_worker.called


@patch.dict(pytailor.config.worker_configurations, mocked_worker_config, clear=True)
@patch("pytailor.cli.main.run_worker")
@patch("pytailor.cli.main.workflow_definition_compliance_test")
def test_worker_config_only(wf_def_check, run_worker):
    runner = CliRunner()
    result = runner.invoke(cli, ["worker",
                                 "--config", "my_config"
                                 ])
    assert result.exit_code == 0
    run_worker.assert_called_once_with(1, 2, "asdf", ["prj_id_1", "prj_id_2"])
    wf_def_check.assert_called_once_with(["prj_id_1", "prj_id_2"])


@patch.dict(pytailor.config.worker_configurations, mocked_worker_config, clear=True)
@patch("pytailor.cli.main.run_worker")
@patch("pytailor.cli.main.workflow_definition_compliance_test")
def test_worker_config_and_args(wf_def_check, run_worker):
    runner = CliRunner()
    result = runner.invoke(cli, ["worker",
                                 "--config", "my_config",
                                 "--sleep", 2,  # will be overwritten by config
                                 "--ncores", 3,  # will be overwritten by config
                                 "--workername", "fdsa",  # will be overwritten
                                 "--project-id-filter", "prj_id_3",  # will be added
                                 "--project-id-filter", "prj_id_4"  # will be added
                                 ])
    assert result.exit_code == 0
    run_worker.assert_called_once_with(
        1, 2, "asdf", ["prj_id_3", "prj_id_4", "prj_id_1", "prj_id_2"])
    wf_def_check.assert_called_once_with(
        ["prj_id_3", "prj_id_4", "prj_id_1", "prj_id_2"])


@patch.dict(pytailor.config.worker_configurations, mocked_worker_config, clear=True)
@patch("pytailor.cli.main.run_worker")
@patch("pytailor.cli.main.workflow_definition_compliance_test")
def test_worker_bad_config_name(wf_def_check, run_worker):
    runner = CliRunner()
    result = runner.invoke(cli, ["worker",
                                 "--config", "non_existing_config"
                                 ])
    assert result.exit_code == 1
    assert str(result.exception) == "No worker configuration found with name " \
                                    "'non_existing_config'"
    assert not run_worker.called
    assert not wf_def_check.called


@patch("builtins.open")
@patch("pathlib.Path.home", return_value=Path("a non existing file"))
def test_init_non_existing_config_file(home, file_open):
    runner = CliRunner()
    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 0
    assert "Created a pyTailor config file at " in result.output
    home.assert_called_once()
    file_open.assert_called_once_with(Path("a non existing file/.tailor/config.toml"),
                                      "w")


@patch("pathlib.Path.exists", return_value=True)
def test_init_existing_config_file(home):
    runner = CliRunner()
    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 0
    assert "A pyTailor config file already exists at " in result.output
    home.assert_called_once()
