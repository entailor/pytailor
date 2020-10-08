import asyncio
import random
import time
from typing import Callable, Any, Union, List, Optional, Awaitable

from pydantic import BaseModel
import httpx

from pytailor.exceptions import BackendResponseError
from pytailor.config import REQUEST_RETRY_COUNT
from pytailor.utils import get_logger


logger = get_logger("RequestHandler")

RETRY_HTTP_CODES = [httpx.codes.BAD_GATEWAY,
                    httpx.codes.FORBIDDEN]


def _get_sleep_time(n):
    return (2 ** n) + (random.randint(0, 300) / 100)


def _handle_retry(exc, no_of_retries):
    """Handle errors which qualify for retry"""
    retry = False
    no_of_retries += 1
    sleep_time = _get_sleep_time(no_of_retries)
    msg = f"Got error: {exc} Retrying in {sleep_time} secs, attempt {no_of_retries}"
    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code in RETRY_HTTP_CODES:
            retry = True
        elif exc.response.status_code == httpx.codes.UNAUTHORIZED:
            # TODO: reauthenticate on expired token
            # retry = True
            # sleep_time = 0.
            # msg = "Token expired, reauthenticating
            pass
    elif isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout)):
        retry = True
    if retry:
        logger.warn(msg)
    return retry, no_of_retries, sleep_time


def _handle_exception(exc, return_none_on, error_msg):
    """Handle errors which do not qualify for retry"""
    if isinstance(exc, httpx.HTTPStatusError):
        if exc.response.status_code in return_none_on:
            return
        error_msg += f" The response from the backend was: {exc}"
        raise BackendResponseError(error_msg)
    elif isinstance(exc, httpx.RequestError):
        error_msg += f" {exc}"
        raise BackendResponseError(error_msg)
    else:
        raise


def handle_request(
    client_method: Callable[..., Union[BaseModel, List[BaseModel]]],
    *args,
    error_msg: str = "Error.",
    return_none_on: Optional[List[httpx.codes]] = None,
) -> Any:

    if return_none_on is None:
        return_none_on = []

    try:
        no_of_retries = 0
        while True:
            try:
                return client_method(*args)
            except Exception as exc:
                retry, no_of_retries, sleep_time = _handle_retry(exc, no_of_retries)
                if not (retry and no_of_retries < REQUEST_RETRY_COUNT):
                    raise
            time.sleep(sleep_time)

    except Exception as exc:
        _handle_exception(exc, return_none_on, error_msg)


async def async_handle_request(
        client_method: Callable[..., Union[Awaitable[BaseModel],
                                           Awaitable[List[BaseModel]]]],
        *args,
        error_msg: str = "Error.",
        return_none_on: Optional[List[httpx.codes]] = None,
) -> Any:
    if return_none_on is None:
        return_none_on = []
    try:
        no_of_retries = 0
        while True:
            try:
                return await client_method(*args)
            except Exception as exc:
                retry, no_of_retries, sleep_time = _handle_retry(exc, no_of_retries)
                if not (retry and no_of_retries < REQUEST_RETRY_COUNT):
                    raise
            await asyncio.sleep(sleep_time)

    except Exception as exc:
        _handle_exception(exc, return_none_on, error_msg)
