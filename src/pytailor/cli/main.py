import click
from multiprocessing import cpu_count
from pytailor.utils import default_worker_name
from pytailor.execution.worker import run_worker


@click.group()
def cli():
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
    "--project-id-filter", default=None, type=str, help="Add a project filter",
    multiple=True
)
def worker(sleep, ncores, workername, project_id_filter):
    run_worker(sleep, ncores, workername, project_id_filter)


if __name__ == '__main__':
    cli()
