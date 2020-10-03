from typing import Callable, Any, Union, List, Optional
from pydantic import BaseModel
import httpx

from pytailor.exceptions import BackendResponseError


def handle_rest_client_call(
    client_method: Callable[..., Union[BaseModel, List[BaseModel]]],
    *args,
    error_msg: str = "Error.",
    return_none_on: Optional[List[httpx.codes]] = None,
) -> Any:
    if return_none_on is None:
        return_none_on = []
    try:
        return client_method(*args)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in return_none_on:
            return
        # TODO handle a 401:
        if exc.response.status_code == httpx.codes.UNAUTHORIZED:
            pass
        error_msg += f" The response from the backend was: {exc}"
        raise BackendResponseError(error_msg)
    except httpx.RequestError as exc:
        error_msg += f" {exc}"
        raise BackendResponseError(error_msg)
    except Exception:
        raise
