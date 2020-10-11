from typing import Optional, List
import httpx

from pytailor.utils import get_logger
from pytailor.models import TaskCheckout, TaskExecutionData
from pytailor.clients import RestClient
from pytailor.common.base import APIBase
from .taskrunner import run_task


class SerialRunner(APIBase):
    def __init__(self, project_id: str, worker_name: str, workflow_id: int,
                 capabilities: List[str] = None):

        self.project_id = project_id
        self.worker_name = worker_name
        self.workflow_id = workflow_id
        self.capabilities = capabilities or ["pytailor"]

    def run(self):

        logger = get_logger("SerialRunner")
        logger.info(f"Starting workflow with id {self.workflow_id}")

        # checkout and run tasks

        checkout_query = TaskCheckout(
            worker_capabilities=self.capabilities,
            worker_name=self.worker_name,
            workflows=[self.workflow_id],
        )

        checkout = self.do_checkout(checkout_query)

        # self.task_service.checkout_ready_task(worker=worker_id, wf_id=wf.id)

        while checkout:
            run_task(checkout)
            checkout = self.do_checkout(checkout_query)

        logger.info(f"Workflow with id {self.workflow_id} finished")

    def do_checkout(self, checkout_query: TaskCheckout) -> Optional[TaskExecutionData]:
        with RestClient() as client:
            return self._handle_request(
                client.checkout_task,
                checkout_query,
                error_msg="Error during task checkout.",
                return_none_on=[httpx.codes.NOT_FOUND],
            )
