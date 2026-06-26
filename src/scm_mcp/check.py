"""连通性与鉴权自检：能拿到 SCM access token 并调通一次 list_jobs 即视为通。

用法:
    python -m scm_mcp.check
退出码:
    0 = 通
    1 = 不通（打印错误原因）
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

    # Step 1: 获取 token
    try:
        token = auth.get_token()
    except Exception as exc:
        print(f"FAIL: 无法获取 SCM access token -> {exc}", file=sys.stderr)
        return 1

    # Step 2: 调一次只读 API 验证 token 有效
    try:
        status, body = rest_client.request("GET", "/config/operations/v1/jobs", params={"limit": 1})
    except Exception as exc:
        print(f"FAIL: 无法调用 SCM API -> {exc}", file=sys.stderr)
        return 1

    if status == 401:
        print(f"FAIL: SCM API 返回 401，token 可能无效或 TSG_ID 不匹配（tsg_id={tsg}）", file=sys.stderr)
        return 1
    if status == 403:
        print(f"FAIL: SCM API 返回 403，服务账号权限不足", file=sys.stderr)
        return 1

    token_preview = token[:8] + "..."
    print(f"OK: SCM API 连通（base={base}, tsg_id={tsg}）")
    print(f"    token={token_preview}  /config/operations/v1/jobs -> HTTP {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
