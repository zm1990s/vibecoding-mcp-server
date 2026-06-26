"""SCM MCP server 入口：官方 mcp SDK + stdio 传输。"""

import asyncio
import json

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from . import tools
from .config import get_base_url

server = Server("scm-mcp")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return tools.TOOLS  # 骨架阶段返回空列表


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    result = await asyncio.to_thread(tools.call, name, arguments)
    return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _run() -> None:
    _ = get_base_url()  # 启动时验证配置可读
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
