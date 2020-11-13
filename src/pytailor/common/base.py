import time
from typing import Any

from .request_handler import handle_request


class APIBase:
    """Base class for classes that interact with backend (makes rest calls)"""

    @staticmethod
    def _handle_request(*args, **kwargs) -> Any:
        return handle_request(*args, **kwargs)
