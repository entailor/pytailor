import click
from multiprocessing import cpu_count
from tailor.utils import default_worker_name
from tailor.execution.worker import run_worker


@click.group()
def cli():
    pass


@cli.command()
@click.option('--sleep', default=3,
              help='sleep time between each job pulling requests (secs)')
@click.option('--ncores', default=cpu_count() - 1, help='max number of parallel jobs')
@click.option('--workername', default=default_worker_name(), help='Provide a worker name')
@click.option('--project', metavar='PROJECTNAME', help='Provide a project name')
def worker(sleep, ncores, workername, project):
    run_worker(sleep, ncores, workername, project)
