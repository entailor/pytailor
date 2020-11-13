import json
import pickle
import uuid
from pathlib import Path
from typing import Optional

import httpx

from pytailor.utils import get_logger
from pytailor.exceptions import AuthenticationError
from pytailor.config import (
    API_IDP_URL,
    API_CLIENT_ID,
    API_WORKER_ID,
    API_SECRET_KEY
)
from pytailor import __version__


COGNITO_HEADERS = {
    "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
    "Content-Type": "application/x-amz-json-1.1",
}
TOKENS_FILE_PATH = Path.home() / ".tailor" / "refresh_token"

# keep access and refresh tokens as global variables
access_token: str = ""
refresh_token: str = ""

logger = get_logger("Auth")


def refresh_tokens(reset_refresh_token: bool = True):
    # refresh/load tokens with the following efforts in order:
    # 1. load tokens from file if they have not already been loaded
    # 2. Try to refresh access token with server using refresh token
    # 3. (Re-) authenticate with server using credentials

    global access_token, refresh_token
    if reset_refresh_token:
        refresh_token = ""

    # no access token in memory
    if not access_token:
        refresh_token = __load_refresh_token_from_file()
        if refresh_token:
            try:
                access_token = __refresh_access_token_from_idp(refresh_token)
                logger.info("Access token refreshed from idp-server")
                return
            except:
                pass

    # Access token in memory, try to refresh access token
    if refresh_token:
        try:
            access_token = __refresh_access_token_from_idp(refresh_token)
            logger.info("Access token refreshed from idp-server")
            return
        except:
            pass

    # 3. (Re-) authenticate
    access_token, refresh_token = __authenticate_with_idp()
    __write_refresh_token_to_file(refresh_token)
    logger.info("Authenticated with idp-server")


def __load_refresh_token_from_file():
    if TOKENS_FILE_PATH.exists():
        with open(TOKENS_FILE_PATH, "rb") as f:
            return pickle.load(f)
    else:
        return ""


def __write_refresh_token_to_file(refresh_token):
    with open(TOKENS_FILE_PATH, "wb") as f:
        TOKENS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        pickle.dump((refresh_token), f)


def __refresh_access_token_from_idp(refresh_token):
    body = {
        "AuthParameters": {
            "REFRESH_TOKEN": refresh_token
        },
        "AuthFlow": "REFRESH_TOKEN_AUTH",
        "ClientId": API_CLIENT_ID
    }
    resp = httpx.post(API_IDP_URL, data=json.dumps(body), headers=COGNITO_HEADERS)
    return resp.json()["AuthenticationResult"]["AccessToken"]


def __authenticate_with_idp():
    body = {
        "AuthParameters": {
            "USERNAME": API_WORKER_ID,
            "PASSWORD": API_SECRET_KEY
        },
        "AuthFlow": "USER_PASSWORD_AUTH",
        "ClientId": API_CLIENT_ID
    }
    resp = httpx.post(API_IDP_URL, data=json.dumps(body), headers=COGNITO_HEADERS)
    payload = resp.json()
    if "AuthenticationResult" not in payload:
        msg = "Could not authenticate."
        if "__type" in payload:
            msg += f" {payload['__type']}: {payload['message']}"
            msg = msg.replace("username", "API_WORKER_ID")
            msg = msg.replace("password", "API_SECRET_KEY")
        raise AuthenticationError(msg)
    return (payload["AuthenticationResult"]["AccessToken"],
            payload["AuthenticationResult"]["RefreshToken"])


class TailorAuth(httpx.Auth):

    def auth_flow(self, request):
        # Add Oauth2 authorization header
        if access_token:
            request.headers["Authorization"] = "Bearer " + access_token
            # Add AWS correlation ID in order to trace requests through the network
            request.headers["X-Amzn-Trace-Id"] = "Root=" + str(uuid.uuid4())
            request.headers["User-Agent"] = "pytailor/" + __version__
            yield request
        else:
            raise AuthenticationError(
                "Could not get access token. Check configuration.")


# try to call refresh_tokens() when module is loaded
try:
    refresh_tokens()
except AuthenticationError as e:
    # credential not configured (expected during unit tests and `tailor init` command)
    logger.error("Could not refresh access token. Check configuration.")
    logger.error(str(e))
