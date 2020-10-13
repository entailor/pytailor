from unittest.mock import patch, MagicMock

import httpx
import pytest
from pytailor.common.request_handler import handle_request, RETRY_HTTP_CODES, \
    RETRY_ERRORS
from pytailor.config import REQUEST_RETRY_COUNT
from pytailor.exceptions import BackendResponseError


def get_http_status_raising_func(error_code):
    response = MagicMock(spec=httpx.Response)
    response.status_code = error_code
    request = MagicMock(spec=httpx.Request)
    request_func = MagicMock()
    request_func.side_effect = httpx.HTTPStatusError(
        str(error_code), request=request, response=response)
    return request_func


def get_http_exception_raising_func(exception):
    request = MagicMock(spec=httpx.Request)
    request_func = MagicMock()
    request_func.side_effect = exception(exception.__name__, request=request)
    return request_func


@patch("pytailor.common.request_handler._get_sleep_time_seconds",
       side_effect=len(RETRY_HTTP_CODES) * REQUEST_RETRY_COUNT * [0])
def test_handle_http_status_retry(_get_sleep_time_seconds, caplog):
    for error_code in RETRY_HTTP_CODES:
        with pytest.raises(BackendResponseError) as e:
            handle_request(
                get_http_status_raising_func(error_code),
                "http://test_url"
            )
        assert str(error_code) in str(e)
    total_retries = REQUEST_RETRY_COUNT * len(RETRY_HTTP_CODES)
    assert _get_sleep_time_seconds.call_count == total_retries
    assert len(caplog.messages) == total_retries


@patch("pytailor.common.request_handler._get_sleep_time_seconds",
       side_effect=len(RETRY_HTTP_CODES) * REQUEST_RETRY_COUNT * [0])
def test_handle_exception_retry(_get_sleep_time_seconds, caplog):
    for exception in RETRY_ERRORS:
        with pytest.raises(BackendResponseError) as e:
            handle_request(
                get_http_exception_raising_func(exception),
                "http://test_url"
            )
        assert exception.__name__ in str(e)
    total_retries = REQUEST_RETRY_COUNT * len(RETRY_ERRORS)
    assert _get_sleep_time_seconds.call_count == total_retries
    assert len(caplog.messages) == total_retries


def test_handle_non_retry_error():
    with pytest.raises(BackendResponseError) as e:
        handle_request(
            get_http_status_raising_func(httpx.codes.NOT_FOUND),
            "http://test_url"
        )
        assert str(httpx.codes.NOT_FOUND) in str(e)


def test_handle_none_on_error():
    code = httpx.codes.NOT_FOUND
    response = handle_request(
        get_http_status_raising_func(code),
        "http://test_url",
        return_none_on=[code]
    )
    assert response is None


@patch("pytailor.common.request_handler.refresh_tokens")
def test_handle_unauthorized(refresh_tokens, caplog):
    code = httpx.codes.UNAUTHORIZED
    with pytest.raises(BackendResponseError) as e:
        response = handle_request(
            get_http_status_raising_func(code),
            "http://test_url",
        )
    assert str(code) in str(e)
    assert refresh_tokens.call_count == REQUEST_RETRY_COUNT