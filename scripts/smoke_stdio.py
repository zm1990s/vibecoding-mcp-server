"""stdio 协议级冒烟：用官方 mcp SDK 的 client over stdio 驱动本 server。

证明本项目作为真实 MCP server 在传输层可用。

流程: 子进程拉起 server -> initialize -> tools/list（断言工具集）-> call list_jobs。

用法:
    python scripts/smoke_stdio.py
依赖: 已 `pip install -e .`；需设置 SCM_CLIENT_ID / SCM_CLIENT_SECRET / SCM_TSG_ID 环境变量。
退出码: 0 = 通过, 1 = 失败。
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXPECTED_TOOLS = {
    # Objects
    "list_addresses", "create_address", "get_address", "update_address", "delete_address",
    "list_address_groups", "create_address_group", "get_address_group", "update_address_group", "delete_address_group",
    "list_services", "create_service",
    "list_service_groups", "create_service_group",
    "list_tags", "create_tag",
    "list_application_groups",
    "list_external_dynamic_lists",
    # Security
    "list_security_rules", "create_security_rule", "get_security_rule", "update_security_rule", "delete_security_rule",
    "list_anti_spyware_profiles", "list_vulnerability_profiles", "list_wildfire_profiles",
    "list_dns_security_profiles", "list_url_categories", "list_decryption_rules", "list_decryption_profiles",
    # Operations
    "list_jobs", "get_job", "list_config_versions", "push_candidate_config",
    # IAM
    "list_service_accounts", "list_roles", "list_access_policies",
}


async def _run() -> int:
    params = StdioServerParameters(command=sys.executable, args=["-m", "scm_mcp.server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("[1] initialize: OK")

            listed = await session.list_tools()
            names = {t.name for t in listed.tools}
            print(f"[2] tools/list: {len(names)} tools")
            if names != EXPECTED_TOOLS:
                missing = EXPECTED_TOOLS - names
                extra = names - EXPECTED_TOOLS
                print(f"    FAIL: expected {len(EXPECTED_TOOLS)} | missing={sorted(missing)} extra={sorted(extra)}", file=sys.stderr)
                return 1
            print(f"    OK: all {len(EXPECTED_TOOLS)} expected tools present")

            result = await session.call_tool("list_jobs", {"limit": 1})
            text = result.content[0].text if result.content else "(empty)"
            print(f"[3] call_tool(list_jobs): {text[:200]}...")

    print("SMOKE OK")
    return 0


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    raise SystemExit(main())
