from unittest.mock import patch ,MagicMock

import httpx
import pytest

from pytailor.common.request_handler import handle_request, RETRY_HTTP_CODES
from pytailor.exceptions import BackendResponseError
from pytailor.config import REQUEST_RETRY_COUNT


def get_http_status_raising_func(error_code):
    response = MagicMock(spec=httpx.Response)
    response.status_code = error_code
    request = MagicMock(spec=httpx.Request)
    request_func = MagicMock()
    request_func.side_effect = httpx.HTTPStatusError(
        str(error_code), request=request, response=response)
    return request_func


def get_http_exception_raising_func(error_code):
    response = MagicMock(spec=httpx.Response)
    response.status_code = error_code
    request = MagicMock(spec=httpx.Request)
    request_func = MagicMock()
    request_func.side_effect = httpx.HTTPStatusError(
        str(error_code), request=request, response=response)
    return request_func


@patch("pytailor.common.request_handler._get_sleep_time",
       side_effect=len(RETRY_HTTP_CODES) * [0, 0, 0, 0, 0])
def test_handle_http_status_retry(_get_sleep_time, caplog):
    for error_code in RETRY_HTTP_CODES:
        with pytest.raises(BackendResponseError) as e:
            handle_request(
                get_http_status_raising_func(error_code),
                "http://test_url"
            )
        assert str(error_code) in str(e)
    total_retries = REQUEST_RETRY_COUNT * len(RETRY_HTTP_CODES)
    assert _get_sleep_time.call_count == total_retries
    assert len(caplog.messages) == total_retries
