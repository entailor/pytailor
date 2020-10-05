from typing import Callable, Any, Union, List, Optional
from pydantic import BaseModel
import httpx

from pytailor.exceptions import BackendResponseError
from .rest_call_handler import handle_rest_client_call


class APIBase:
    """Base class for classes that interact with backend (makes rest calls)"""

    @staticmethod
    def _handle_rest_client_call(*args, **kwargs) -> Any:
        return handle_rest_client_call(*args, **kwargs)
