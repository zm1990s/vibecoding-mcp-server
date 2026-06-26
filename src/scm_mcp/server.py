"""SCM MCP server 入口：官方 mcp SDK + stdio 传输。"""

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from . import tools
from .config import get_base_url

server = Server("scm-mcp")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return tools.TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    result = await asyncio.to_thread(tools.call, name, arguments)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    return [types.TextContent(type="text", text=text)]


async def _run() -> None:
    _ = get_base_url()
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
