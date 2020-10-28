import time
from typing import Any

from pytailor.exceptions import BackendResponseError
from pytailor.models import TaskExecutionData, ProcessingStatus
from pytailor.config import WAIT_RETRY_COUNT

from .request_handler import handle_request


class APIBase:
    """Base class for classes that interact with backend (makes rest calls)"""

    @staticmethod
    def _handle_request(*args, **kwargs) -> Any:
        return handle_request(*args, **kwargs)

    def _wait_for_exec_data(self, *args, **kwargs) -> Any:
        time.sleep(2.)
        response = self._handle_request(*args, **kwargs)
        if response.processing_status is ProcessingStatus.PENDING:
            retries = 0
            while response.processing_status is ProcessingStatus.PENDING:
                print("waiting for backend result")
                time.sleep(2.)
                retries += 1
                response = self._handle_request(*args, **kwargs)
                if retries > WAIT_RETRY_COUNT:
                    raise BackendResponseError("Failed to retrieve result from "
                                               "backend")
        return response
