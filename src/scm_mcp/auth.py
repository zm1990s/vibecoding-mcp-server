"""SCM OAuth2 client_credentials 令牌管理。

token 有效期 15 分钟；提前 60 秒刷新，避免边界竞争。
threading.Lock 保证并发调用安全。
"""

import threading
import time

import httpx

from . import config

_REFRESH_BUFFER = 60  # 提前 60 秒刷新

_lock = threading.Lock()
_token: str | None = None
_expires_at: float = 0.0


def _fetch_token() -> tuple[str, float]:
    """向 SCM Auth Service 请求新 access token，返回 (token, expires_at)。"""
    url = f"{config.get_auth_url()}/auth/v1/oauth2/access_token"
    data = {
        "grant_type": "client_credentials",
        "scope": f"tsg_id:{config.get_tsg_id()}",
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            url,
            data=data,
            auth=(config.get_client_id(), config.get_client_secret()),
        )
        resp.raise_for_status()
        body = resp.json()

    token = body["access_token"]
    expires_in = int(body.get("expires_in", 900))
    expires_at = time.monotonic() + expires_in - _REFRESH_BUFFER
    return token, expires_at


def get_token() -> str:
    """返回有效的 Bearer token，必要时自动刷新（线程安全）。"""
    global _token, _expires_at
    with _lock:
        if _token is None or time.monotonic() >= _expires_at:
            _token, _expires_at = _fetch_token()
        return _token


def bearer_headers() -> dict[str, str]:
    """返回含 Authorization: Bearer <token> 的 headers 字典。"""
    return {"Authorization": f"Bearer {get_token()}"}
