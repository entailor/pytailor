# -*- coding: utf-8 -*-

import argparse
import asyncio
import concurrent.futures
import logging
import platform
import uuid
from multiprocessing import cpu_count
from typing import Optional

from tailor.config import LOGGING_FORMAT
from tailor.execution.taskrunner import run_task
from tailor.models import TaskCheckout, TaskExecutionData
from tailor.utils import get_logger
from tailor.clients import AsyncRestClient


async def do_checkout(checkout_query: TaskCheckout
                      ) -> Optional[TaskExecutionData]:
    async with AsyncRestClient() as client:
        exec_data = await client.checkout_task(checkout_query)
    return exec_data


async def async_run_task(pool, task_execution_data: TaskExecutionData):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(pool, run_task, task_execution_data)
    return result


# job run-manager
async def run_manager(checkout_query: TaskCheckout, worker, n_cores, sleep):
    # use default project if not provided

    # set up logging
    core_report_format = LOGGING_FORMAT + f' (%(n)s/{n_cores} cores in use)'
    formatter = logging.Formatter(core_report_format)
    logger = get_logger('Worker', formatter=formatter)
    n_running = 0
    extra = {'n': n_running}
    logger = logging.LoggerAdapter(logger, extra)

    # helper to handle finished asyncio_tasks
    def handle_finished(aio_tasks):
        for aio_task in list(aio_tasks):
            if aio_task.done():
                aio_tasks.remove(aio_task)
                print('Task finished', aio_task.result())

    # go into loop with process pool
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_cores) as pool:
        try:
            asyncio_tasks = set()
            while True:
                n_running = len(asyncio_tasks)
                extra['n'] = n_running  # update running for logging
                if n_running < n_cores:
                    # look for READY job
                    task_exec_data = await do_checkout(checkout_query)
                    if task_exec_data:
                        logger.info(
                            f'Task available, starting run for task'
                            f'{task_exec_data.task.id}')
                        asyncio_task = asyncio.create_task(async_run_task(
                            pool, task_exec_data))
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


def run_worker(sleep, n_cores, worker_name):
    checkout_query = TaskCheckout(
        worker_capabilities=['python'],
        worker_name=worker_name,
    )

    try:
        asyncio.run(
            run_manager(checkout_query, worker_name, int(n_cores), int(sleep))
        )
    except KeyboardInterrupt:
        print("CTRL-C pressed, exiting...")
