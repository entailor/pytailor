import asyncio
import concurrent.futures
import logging
from typing import Optional, List
import httpx

from pytailor.config import LOGGING_FORMAT
from pytailor.execution.taskrunner import run_task
from pytailor.models import TaskCheckout, TaskExecutionData
from pytailor.utils import get_logger
from pytailor.clients import AsyncRestClient
from pytailor.exceptions import BackendResponseError
from pytailor.common.request_handler import async_handle_request


async def do_checkout(checkout_query: TaskCheckout) -> Optional[TaskExecutionData]:
    async with AsyncRestClient() as client:
        return await async_handle_request(
            client.checkout_task,
            checkout_query
        )


async def async_run_task(pool, task_execution_data: TaskExecutionData, logger):
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(pool, run_task, task_execution_data)
    except Exception as e:
        logger.exception(msg="Unexpected error during task execution", exc_info=e)


# job run-manager
async def run_manager(checkout_query: TaskCheckout, n_cores, sleep):

    # set up logging
    core_report_format = LOGGING_FORMAT + f" (%(n)s/{n_cores} cores in use)"
    formatter = logging.Formatter(core_report_format)
    logger = get_logger("Worker", formatter=formatter)
    n_running = 0
    extra = {"n": n_running}
    logger = logging.LoggerAdapter(logger, extra)

    # helper to handle finished asyncio_tasks
    def handle_finished(aio_tasks):
        for aio_task in list(aio_tasks):
            if aio_task.done():
                aio_tasks.remove(aio_task)

    # go into loop with process pool
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_cores) as pool:
        try:

            asyncio_tasks = set()

            while True:

                n_running = len(asyncio_tasks)
                extra["n"] = n_running  # update running for logging

                if n_running < n_cores:
                    # worker can checkout task
                    task_exec_data = await do_checkout(checkout_query)

                    if task_exec_data:
                        logger.info(
                            f"Task available, starting run for task "
                            f"{task_exec_data.task_id}"
                        )
                        asyncio_task = asyncio.create_task(
                            async_run_task(pool, task_exec_data, logger)
                        )
                        asyncio_tasks.add(asyncio_task)
                        handle_finished(asyncio_tasks)

                    else:
                        logger.info(f"No jobs available, waiting {sleep} seconds")
                        await asyncio.sleep(sleep)
                        handle_finished(asyncio_tasks)

                else:
                    logger.info(f"All cores in use, waiting {sleep} seconds")
                    await asyncio.sleep(sleep)
                    handle_finished(asyncio_tasks)

        except asyncio.CancelledError:
            pass  # TODO recover or die?
            # print('\excepted CanceledError\n')

        # TODO: do graceful handling of non-finished tasks on worker errors, e.g:
        #       - try to checkin FAILED with a meaningful error message,
        #       - or try to reset tasks for re-execution elsewhere


def run_worker(sleep, n_cores, worker_name, project_ids, capabilities: List[str]):
    if "pytailor" not in capabilities:
        capabilities.append("pytailor")
    checkout_query = TaskCheckout(
        worker_capabilities=capabilities,
        worker_name=worker_name,
        projects=project_ids or None,
    )

    try:
        asyncio.run(run_manager(checkout_query, n_cores, sleep))
    except KeyboardInterrupt:
        print("CTRL-C pressed, exiting...")
