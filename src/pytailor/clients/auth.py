import uuid

import httpx


class TailorAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        # Add Oauth2 authorization header
        request.headers["Authorization"] = "Bearer " + self.token
        # Add AWS correlation ID in order to trace requests through the network
        request.headers["X-Amzn-Trace-Id"] = str(uuid.uuid4())
        yield request
