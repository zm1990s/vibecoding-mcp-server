"""测试脚手架：mock REST 层，单测不依赖 SCM 在线。

fixture `mock_rest`：注册 (METHOD, PATH) -> 响应，
monkeypatch 掉 rest_client 中的 httpx.Client，使被测代码走 mock 传输。
"""

import json as _json

import httpx
import pytest

from scm_mcp import rest_client


class _Router:
    def __init__(self):
        self._routes: dict = {}
        self.requests: list = []

    def add(self, method: str, path: str, *, status: int = 200, json=None, text=None):
        self._routes[(method.upper(), path)] = (status, json, text)

    def _handler(self, request: httpx.Request) -> httpx.Response:
        try:
            body = _json.loads(request.content) if request.content else None
        except ValueError:
            body = None
        self.requests.append({
            "method": request.method.upper(),
            "path": request.url.path,
            "params": dict(request.url.params),
            "json": body,
        })
        key = (request.method.upper(), request.url.path)
        if key not in self._routes:
            return httpx.Response(404, json={"detail": f"no mock for {key}"})
        status, json_body, text_body = self._routes[key]
        if text_body is not None:
            return httpx.Response(status, text=text_body)
        return httpx.Response(
            status,
            content=_json.dumps(json_body).encode(),
            headers={"content-type": "application/json"},
        )

    def client(self) -> httpx.Client:
        return httpx.Client(base_url="http://mock", transport=httpx.MockTransport(self._handler))


@pytest.fixture
def mock_rest(monkeypatch):
    router = _Router()

    def _patched_request(method, full_path, *, params=None, json=None):
        with router.client() as c:
            resp = c.request(method, full_path, params=params, json=json)
            try:
                return resp.status_code, resp.json()
            except ValueError:
                return resp.status_code, resp.text

    monkeypatch.setattr(rest_client, "request", _patched_request)
    return router
