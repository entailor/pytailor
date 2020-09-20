import httpx

from pytailor.config import AUTH_KEY


class TailorAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        # Send the request, with an `Authorization` header.
        request.headers["Authorization"] = "Bearer " + self.token
        yield request
