from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import requests
from . import __name__ as _svc

def build_authorize_url(app, state: str) -> str:
    qs = {
        "response_type": "code",
        "client_id": app.config["MELI_CLIENT_ID"],
        "redirect_uri": app.config["MELI_REDIRECT_URI"],
        "state": state,
        # Include if your app is configured for refresh tokens:
        # "scope": "offline_access"
    }
    return f'{app.config["MELI_AUTHORIZE_URL"]}?{urlencode(qs)}'

def exchange_code_for_token(app, code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "client_id": app.config["MELI_CLIENT_ID"],
        "client_secret": app.config["MELI_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": app.config["MELI_REDIRECT_URI"],
    }
    r = requests.post(app.config["MELI_TOKEN_URL"], data=data, timeout=20)
    r.raise_for_status()
    return r.json()

def refresh_access_token(app, refresh_token: str) -> dict:
    data = {
        "grant_type": "refresh_token",
        "client_id": app.config["MELI_CLIENT_ID"],
        "client_secret": app.config["MELI_CLIENT_SECRET"],
        "refresh_token": refresh_token,
    }
    r = requests.post(app.config["MELI_TOKEN_URL"], data=data, timeout=20)
    r.raise_for_status()
    return r.json()

def compute_expiry(expires_in: int) -> datetime:
    # subtract 60s to renew slightly early
    return datetime.now(timezone.utc) + timedelta(seconds=max(0, expires_in - 60))

def get_me(access_token: str) -> (dict, int):
    r = requests.get(
        "https://api.mercadolibre.com/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20
    )
    return r.json(), r.status_code
