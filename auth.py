import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from models import Config

SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"


def authenticate(config: Config) -> Credentials:
    creds = None

    if Path(config.token_store_path).exists():
        creds = Credentials.from_authorized_user_file(config.token_store_path, scopes=[SCOPE])

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_credentials(creds, config.token_store_path)
        return creds

    flow = InstalledAppFlow.from_client_secrets_file(
        config.client_secrets_path,
        scopes=[SCOPE],
    )
    creds = flow.run_local_server(port=0)
    _save_credentials(creds, config.token_store_path)

    return creds


def _save_credentials(creds: Credentials, token_store_path: str) -> None:
    Path(token_store_path).parent.mkdir(parents=True, exist_ok=True)
    with open(token_store_path, "w") as f:
        f.write(creds.to_json())
