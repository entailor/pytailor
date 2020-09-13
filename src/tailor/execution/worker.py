# -*- coding: utf-8 -*-

import argparse
import asyncio
import concurrent.futures
import logging
import platform
import uuid
from multiprocessing import cpu_count

from tailor.config import LOGGING_FORMAT
from tailor.execution.taskrunner import run_task
from tailor.models import TaskCheckout
from tailor.utils import get_logger


def do_checkout():


async def async_run_task(pool, project_uuid: str, task):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(pool, run_task, project_uuid, task)
    return result


# job run-manager
async def run_manager(project_uuid: str, worker, ncores, sleep):
    # use default project if not provided

    # set up logging
    core_report_format = LOGGING_FORMAT + f' (%(n)s/{ncores} cores in use, ' + 'prj: %(prj)s)'
    formatter = logging.Formatter(core_report_format)
    logger = get_logger(f'{project_uuid}', formatter=formatter)
    nrunning = 0
    extra = {'n': nrunning, 'prj': project_uuid}
    logger = logging.LoggerAdapter(logger, extra)

    single_task_service = SingleTaskService()

    # helper to handle finished asyncio_tasks
    def handle_finished(aio_tasks):
        for aio_task in list(aio_tasks):
            if aio_task.done():
                aio_tasks.remove(aio_task)
                print('Task finished', aio_task.result())

    # go into loop with process pool
    with concurrent.futures.ProcessPoolExecutor(max_workers=ncores) as pool:
        try:
            asyncio_tasks = set()
            while True:
                nrunning = len(asyncio_tasks)
                extra['n'] = nrunning  # update running for logging
                if nrunning < ncores:
                    # look for READY job
                    single_task = single_task_service.checkout_ready_task(worker=worker)
                    if single_task:
                        logger.info(
                            f'Job available, starting run for job {single_task.id}')
                        asyncio_task = asyncio.create_task(async_run_task(
                            pool, project_uuid, single_task))
                        asyncio_tasks.add(asyncio_task)
                        # use a shorter fixed sleep time here in order to start
                        # jobs faster when many are available
                        await asyncio.sleep(.3)
                        handle_finished(asyncio_tasks)
                    else:
                        logger.info(f'No jobs available, waiting {sleep} seconds')
                        await asyncio.sleep(sleep)
                        handle_finished(asyncio_tasks)
                else:
                    logger.info(f'All cores in use, waiting {sleep} seconds')
                    await asyncio.sleep(sleep)
                    handle_finished(asyncio_tasks)

        except asyncio.CancelledError:
            pass  # TODO recover or die?
            # print('\excepted CanceledError\n')


def run_worker(sleep, ncores, worker_name, project):

    checkout_query = TaskCheckout(
        worker_capabilities=['python'],
        worker_name=worker_name,
    )

    try:
        asyncio.run(
            run_manager(project, worker_name, int(ncores), int(sleep))
        )
    except KeyboardInterrupt:
        print("CTRL-C pressed, exiting...")
