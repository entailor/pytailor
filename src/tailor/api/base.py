from typing import Callable, Any, Union, List
from httpx import RequestError, HTTPStatusError
from pydantic import BaseModel

from tailor.exceptions import BackendResponseError


class APIBase:
    """Base class for all tailor.api classes that interact with backend"""

    @staticmethod
    def _handle_rest_client_call(client_method: Callable[..., Union[BaseModel,
                                                                    List[BaseModel]]],
                                 *args,
                                 error_msg: str = 'Error.',
                                 ) -> Any:
        try:
            return client_method(*args)
        except HTTPStatusError as exc:
            # TODO handle a 401
            error_msg += f' The response from the backend was: {exc}'
            raise BackendResponseError(error_msg)
        except RequestError as exc:
            error_msg += f' The response from the backend was: {exc}'
            raise BackendResponseError(error_msg)
        except Exception:
            raise
