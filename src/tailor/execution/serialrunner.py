from typing import Optional
import httpx

from tailor.utils import get_logger
from tailor.models import TaskCheckout, TaskExecutionData
from tailor.clients import RestClient
from .taskrunner import run_task


class SerialRunner:

    def __init__(self,
                 project_id: str,
                 worker_name: str,
                 workflow_id: int
                 ):

        self.project_id = project_id
        self.worker_name = worker_name
        self.workflow_id = workflow_id

    def run(self):

        logger = get_logger('SerialRunner')
        logger.info(f'Starting workflow with id {self.workflow_id}')

        # checkout and run tasks

        checkout_query = TaskCheckout(
            worker_capabilities=['python'],
            worker_name=self.worker_name,
            # workflows=[self.workflow_id]
        )

        checkout = self.do_checkout(checkout_query)

        # self.task_service.checkout_ready_task(worker=worker_id, wf_id=wf.id)

        while checkout:
            run_task(checkout, self.project_id)
            checkout = self.do_checkout(checkout_query)

        logger.info(f'Workflow with id {self.workflow_id} finished')

    def do_checkout(self, checkout_query: TaskCheckout
                    ) -> Optional[TaskExecutionData]:
        with RestClient() as client:
            # return client.checkout_task(checkout_query)

            try:
                return client.checkout_task(checkout_query)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == httpx.codes.NOT_FOUND:
                    return None  # expected, no more tasks to run
                else:
                    raise