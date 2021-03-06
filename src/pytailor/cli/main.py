import click
from multiprocessing import cpu_count
from pathlib import Path
import toml

from pytailor.utils import default_worker_name
from pytailor.execution.worker import run_worker
from pytailor.execution.worker_checks import workflow_definition_compliance_test
import pytailor.config


@click.group()
def cli():
    """A command-line interface for pyTailor."""
    pass


@cli.command()
@click.option(
    "--sleep", default=3.0, type=float,
    help="sleep time between each task checkout request (secs)"
)
@click.option("--ncores", default=cpu_count() - 1, type=int,
              help="max number of parallel jobs")
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
    default=False,
    help="Perform checks to validate the worker environment before starting the worker"
)
@click.option(
    "--checks-only", is_flag=True, help="Perform checks without starting the worker"
)
@click.option(
    "--capability",
    default=None,
    type=str,
    help="Specify a worker capability",
    multiple=True,
)
@click.option(
    "--config",
    type=str,
    default=None,
    help="Use a worker configuration from the Tailor config file"
)
def worker(sleep, ncores, workername, project_id_filter, checks, checks_only,
           capability, config):
    """Start a worker process."""

    project_ids = list(project_id_filter) if project_id_filter else []
    capabilities = list(capability) if capability else []

    if config:
        worker_config = pytailor.config.worker_configurations.get(config)
        if worker_config:
            sleep = worker_config.get("sleep") or sleep
            ncores = worker_config.get("ncores") or ncores
            workername = worker_config.get("workername") or workername
            project_ids += worker_config.get("project_ids") or []
            capabilities += worker_config.get("capabilities") or []
        else:
            raise ValueError(f"No worker configuration found with name '{config}'")

    if checks:
        # check compliance with project wf defs
        wf_defs_info = workflow_definition_compliance_test(project_ids)
        # TODO: create a wf_def_filter based on wf_defs_info ?

    if checks_only:
        if not checks:
            wf_defs_info = workflow_definition_compliance_test(project_ids)
        return

    run_worker(sleep, ncores, workername, project_ids, capabilities)


@cli.command()
def init():
    """Create a template config file"""
    config_file = Path.home() / ".tailor" / "config.toml"
    if config_file.exists():
        print(f"A pyTailor config file already exists at {config_file}")
    else:
        config_file.parent.mkdir(parents=True, exist_ok=True)
        toml.dump(
            {
                "pytailor": {
                    "API_WORKER_ID": "<API WORKER ID HERE>",
                    "API_SECRET_KEY": "<API SECRET KEY HERE>",
                },
                "worker": {
                    "my_config": {
                        "sleep": 3,
                        "ncores": cpu_count() - 1,
                        "workername": "my_worker",
                        "project_ids": [],
                        "capabilities": [],
                    }
                },
            },
            open(config_file, "w"),
        )
        print(f"Created a pyTailor config file at {config_file}")


if __name__ == "__main__":
    cli()
