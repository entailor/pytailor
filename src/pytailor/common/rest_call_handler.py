import asyncio
import time
from typing import Callable, Any, Union, List, Optional, Awaitable
from pydantic import BaseModel
import httpx

from pytailor.exceptions import BackendResponseError
from pytailor.config import API_CALL_RETRY_COUNT
from pytailor.utils import get_logger


logger = get_logger("APICallHandler")

retry_http_codes = [httpx.codes.BAD_GATEWAY]


def _handle_exception(exc, return_none_on, error_msg):

    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code in return_none_on:
            return
        # TODO handle a 401:
        if exc.response.status_code == httpx.codes.UNAUTHORIZED:
            pass
        error_msg += f" The response from the backend was: {exc}"
        raise BackendResponseError(error_msg)
    elif isinstance(exc, httpx.RequestError):
        error_msg += f" {exc}"
        raise BackendResponseError(error_msg)
    else:
        raise


def handle_rest_client_call(
    client_method: Callable[..., Union[BaseModel, List[BaseModel]]],
    *args,
    error_msg: str = "Error.",
    return_none_on: Optional[List[httpx.codes]] = None,
) -> Any:

    if return_none_on is None:
        return_none_on = []

    try:
        retries = 0
        while True:
            try:
                return client_method(*args)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in retry_http_codes:
                    retries += 1
                    logger.warn(
                        f"Got error: {exc} Retrying in 2 secs, attempt {retries}"
                    )
                    time.sleep(2)
                    if retries >= API_CALL_RETRY_COUNT:
                        raise
                else:
                    raise

    except Exception as exc:
        _handle_exception(exc, return_none_on, error_msg)


async def async_handle_rest_client_call(
        client_method: Callable[..., Union[Awaitable[BaseModel],
                                           Awaitable[List[BaseModel]]]],
        *args,
        error_msg: str = "Error.",
        return_none_on: Optional[List[httpx.codes]] = None,
) -> Any:
    if return_none_on is None:
        return_none_on = []
    try:
        retries = 0
        while True:
            try:
                return await client_method(*args)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in retry_http_codes:
                    retries += 1
                    logger.warn(
                        f"Got error: {exc} Retrying in 2 secs, attempt {retries}"
                    )
                    await asyncio.sleep(2)
                    if retries >= API_CALL_RETRY_COUNT:
                        raise
                else:
                    raise

    except Exception as exc:
        _handle_exception(exc, return_none_on, error_msg)
