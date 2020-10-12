import httpx
from pytailor.models import *
from pytailor.config import (
    API_BASE_URL,
    ASYNC_REQUEST_TIMEOUT,
    ASYNC_CONNECT_TIMEOUT,
)
from .auth import TailorAuth


class AsyncRestClient(httpx.AsyncClient):
    def __init__(self):
        timeout = httpx.Timeout(
            timeout=ASYNC_REQUEST_TIMEOUT, connect=ASYNC_CONNECT_TIMEOUT
        )
        super().__init__(
            base_url=API_BASE_URL, auth=TailorAuth(), timeout=timeout
        )

    async def checkout_task(
        self, checkout_query: TaskCheckout
    ) -> Optional[TaskExecutionData]:
        url = f"tasks/checkouts"
        response = await self.post(url, data=checkout_query.json())
        if response.status_code == httpx.codes.OK:
            return TaskExecutionData.parse_obj(response.json())
        elif response.status_code == httpx.codes.NOT_FOUND:
            return None
        else:
            response.raise_for_status()
