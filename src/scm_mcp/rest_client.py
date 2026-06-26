"""SCM REST API 薄封装。

职责：注入 Bearer token，发出 HTTP 请求，返回 (status_code, body)。
非 2xx 不抛异常——交由 tools 层组装结构化错误。
"""

import httpx

from . import auth, config

_TIMEOUT = 30.0


def _parse_body(resp: httpx.Response) -> object:
    try:
        return resp.json()
    except ValueError:
        return resp.text


def request(
    method: str,
    full_path: str,
    *,
    params: dict | None = None,
    json: dict | None = None,
) -> tuple[int, object]:
    """发一次 REST 请求，返回 (status_code, body)。

    full_path 示例："/config/objects/v1/addresses"
    """
    url = config.get_base_url() + full_path
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.request(
            method,
            url,
            headers=auth.bearer_headers(),
            params=params,
            json=json,
        )
        return resp.status_code, _parse_body(resp)
