import click
from multiprocessing import cpu_count
from pathlib import Path
import toml

from pytailor.utils import default_worker_name
from pytailor.execution.worker import run_worker
from pytailor.execution.worker_checks import workflow_definition_compliance_test


@click.group()
def cli():
    """A command-line interface for pyTailor."""
    pass


@cli.command()
@click.option(
    "--sleep", default=3, help="sleep time between each task checkout request (secs)"
)
@click.option("--ncores", default=cpu_count() - 1, help="max number of parallel jobs")
@click.option(
    "--workername", default=default_worker_name(), help="Provide a worker name"
)
@click.option(
    "--project-id-filter",
    default=None,
    type=str,
    help="Add a project filter",
    multiple=True,
)
@click.option(
    "--checks/--no-checks",
    default=True,
    help="Perform checks to validate the worker environment before starting the worker"
)
@click.option(
    "--checks-only", is_flag=True, help="Perform checks without starting the worker"
)
def worker(sleep, ncores, workername, project_id_filter, checks, checks_only):
    """Start a worker process."""
    if checks:
        # check compliance with project wf defs
        wf_defs_info = workflow_definition_compliance_test(project_id_filter)
        # TODO: create a wf_def_filter based on wf_defs_info ?

    if checks_only:
        return
    run_worker(sleep, ncores, workername, project_id_filter)


@cli.command()
def init():
    """Create a template config file"""
    config_file = Path.home() / ".tailor" / "config.toml"
    if config_file.exists():
        print(f"A pyTailor config file already exists at {config_file}")
    else:
        toml.dump(
            {
                "pytailor": {
                    "AUTH_KEY": "<PUT YOUR AUTH-KEY HERE>",
                    "API_BASE_URL": "<API BASE URL HERE>",
                },
                "worker": {
                    "my_config": {
                        "sleep": 3,
                        "ncores": cpu_count() - 1,
                        "workername": "my_worker",
                        "capabilities": ["python"],
                        "project_ids": [],
                        "workflow_definition_ids": [],
                        "workflow_ids": [],
                    }
                },
            },
            open(config_file, "w"),
        )
        print(f"Created a pyTailor config file at {config_file}")


if __name__ == "__main__":
    cli()
