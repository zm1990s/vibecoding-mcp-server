"""stdio 协议级冒烟：验证 server 可启动、tools/list 返回空列表（骨架阶段）。

用法：
    python scripts/smoke_stdio.py
依赖：已 `pip install -e .`
退出码：0 = 通过，1 = 失败
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def _run() -> int:
    params = StdioServerParameters(command=sys.executable, args=["-m", "scm_mcp.server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("[1] initialize: OK")

            listed = await session.list_tools()
            count = len(listed.tools)
            print(f"[2] tools/list: {count} tools")

            if count != 0:
                names = [t.name for t in listed.tools]
                print(f"    FAIL: 骨架阶段期望 0 个 tool，实际得到 {count}: {names}", file=sys.stderr)
                return 1

            print("    OK: tools/list 返回空列表（骨架阶段符合预期）")

    print("SMOKE OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_run()))
