import click
from multiprocessing import cpu_count
from pytailor.utils import default_worker_name
from pytailor.execution.worker import run_worker


@click.group()
def cli():
    pass


@cli.command()
@click.option('--sleep', default=3,
              help='sleep time between each task checkout request (secs)')
@click.option('--ncores', default=cpu_count() - 1, help='max number of parallel jobs')
@click.option('--workername', default=default_worker_name(), help='Provide a worker name')
def worker(sleep, ncores, workername):
    run_worker(sleep, ncores, workername)
