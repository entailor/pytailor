import httpx

from tailor.config import API_BASE_URL, AUTH_KEY


class TailorAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        # Send the request, with a custom `X-Authentication` header.
        request.headers['Authorization'] = 'Bearer ' + self.token
        yield request


client = httpx.Client(base_url=API_BASE_URL, auth=TailorAuth(AUTH_KEY))
