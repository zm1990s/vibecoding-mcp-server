"""SCM REST API 的薄封装。

职责：
- 自动注入 Bearer token（via auth.bearer_headers）。
- 不含任何业务逻辑；只做「发请求 → 返回 (status, body)」。
- 非 2xx 不抛异常，交给 tools 层组装结构化错误。

SCM config API 的 base URL 示例：
  https://api.strata.paloaltonetworks.com/config/objects/v1
  https://api.strata.paloaltonetworks.com/config/security/v1
  https://api.strata.paloaltonetworks.com/config/operations/v1
  https://api.strata.paloaltonetworks.com/iam/v1

调用方传入 full_path（已含 /config/objects/v1/addresses 这类路径前缀），
本模块拼 SCM_BASE_URL + full_path 后发出请求。
"""

import httpx

from . import auth, config

DEFAULT_TIMEOUT = 30.0


def _body(resp: httpx.Response):
    """优先 JSON 解析，失败则回退原始文本。"""
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
    headers = auth.bearer_headers()
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        resp = client.request(method, url, headers=headers, params=params, json=json)
        return resp.status_code, _body(resp)
