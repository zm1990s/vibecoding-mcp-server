"""连通性自检：获取 token + 调一次 GET /config/operations/v1/jobs。

用法：
    python -m scm_mcp.check
退出码：
    0 = 连通正常
    1 = 失败（打印原因到 stderr）
"""

import sys

from . import auth, rest_client
from .config import get_base_url, get_tsg_id


def main() -> int:
    base = get_base_url()

    try:
        tsg = get_tsg_id()
    except RuntimeError as exc:
        print(f"FAIL: 配置缺失 -> {exc}", file=sys.stderr)
        return 1

    try:
        auth.get_token()
    except Exception as exc:
        print(f"FAIL: 无法获取 SCM access token -> {exc}", file=sys.stderr)
        return 1

    try:
        status, body = rest_client.request(
            "GET", "/config/operations/v1/jobs", params={"limit": 1}
        )
    except Exception as exc:
        print(f"FAIL: 无法调用 SCM API -> {exc}", file=sys.stderr)
        return 1

    if status == 401:
        print(f"FAIL: 401 Unauthorized（tsg_id={tsg}）", file=sys.stderr)
        return 1
    if status == 403:
        print(f"FAIL: 403 Forbidden — 服务账号权限不足（tsg_id={tsg}）", file=sys.stderr)
        return 1
    if status >= 400:
        print(f"FAIL: HTTP {status} -> {body}", file=sys.stderr)
        return 1

    print(f"OK: SCM API 连通（base={base}, tsg_id={tsg}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
