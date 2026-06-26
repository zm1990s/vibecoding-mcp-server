"""MCP tool 定义与分发——骨架占位。

TOOLS 当前为空列表；tool↔REST 端点映射填充是 WORKFLOW.md 阶段 1 的第一步。
"""

import mcp.types as types

# _TBD_：阶段 1 契约同步完成后，按 DESIGN.md §3 逐条注册。
TOOLS: list[types.Tool] = []

# _TBD_：阶段 1 完成后，按 DESIGN.md §3 填充路由表。
_REGISTRY: dict = {}


def call(name: str, arguments: dict) -> object:
    """分发 tool 调用——当前无已注册 tool。"""
    raise NotImplementedError(f"tool '{name}' not implemented (_TBD_)")
