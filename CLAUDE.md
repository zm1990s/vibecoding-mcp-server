# CLAUDE.md — L1 工程契约

> 本文件是项目的最高约束（L1）。L2（`DESIGN.md`）、L3（`WORKFLOW.md`）必须服从本文件。
> 当任何下层文档或代码与本文件冲突时，以本文件为准。

## 1. 项目身份

本项目是一个 **MCP server**，把 **Palo Alto Networks Strata Cloud Manager（SCM）** 的 REST API，封装成一组 MCP tools，供 Claude Desktop / Cursor 等 MCP 客户端调用。

它**不是**新平台、**不是**业务后端、**不是** REST 网关重写。它只是 SCM REST API 的一层 MCP 适配壳。

## 2. 技术栈（钉死，不许更换）

| 项 | 选定 | 说明 |
| --- | --- | --- |
| 语言 | **Python 3.10+** | 不引入其他语言 |
| MCP 框架 | **官方 `mcp` SDK** | 不用第三方 MCP 实现 |
| 传输 | **stdio** | 只此一种，不加 HTTP/SSE/WebSocket 传输 |
| HTTP 客户端 | **`httpx`** | 调 SCM REST 用 |

> 如需更换上述任一项，必须先改本文件并说明理由，不得在代码里悄悄替换。

## 3. 目录约定

```
scm-mcp-server/
├── CLAUDE.md              # L1 工程契约（本文件）
├── DESIGN.md              # L2 设计：MCP tool ↔ REST 端点映射
├── WORKFLOW.md            # L3 阶段协议
├── README.md              # 给人看：怎么跑、怎么注册
├── .env.example           # 环境变量示例
├── docs/                  # 补充文档
├── scripts/
│   └── smoke_stdio.py     # stdio 协议级冒烟
├── tests/                 # pytest 单测（mock REST）+ 可选 @integration
└── src/scm_mcp/           # 代码
    ├── __init__.py
    ├── server.py          # MCP server 入口
    ├── config.py          # 环境变量读取
    ├── auth.py            # OAuth2 client_credentials token 管理
    ├── rest_client.py     # SCM REST 薄封装
    ├── tools.py           # MCP tool 定义与分发
    └── check.py           # 连通性自检
```

## 4. 禁止事项（红线）

- ❌ **不手抄、不臆造 schema**。所有 tool 的入参/出参 schema，唯一权威来源是 `openapi-specs/scm/` 下的 YAML 文件。
- ❌ **不重写 SCM 业务逻辑**。MCP tool 只做「组装请求 → 调 REST → 透传结果」。
- ❌ **不硬编码 base URL 与凭据**。地址和凭据一律走环境变量（见下）。
- ❌ **不增加传输方式**。只 stdio。
- ❌ **不绕过 REST 直连数据库 / 文件系统**。

## 5. 必须执行

- ✅ SCM 凭据通过 `SCM_CLIENT_ID` / `SCM_CLIENT_SECRET` / `SCM_TSG_ID` 读取。
- ✅ SCM API 基址通过 `SCM_BASE_URL` 读取，默认 `https://api.strata.paloaltonetworks.com`。
- ✅ Auth URL 通过 `SCM_AUTH_URL` 读取，默认 `https://auth.apps.paloaltonetworks.com`。
- ✅ 每个 MCP tool 必须能一一追溯到 `DESIGN.md §3` 中的一个具体 REST 端点（方法 + 路径）。
- ✅ access token 由 `auth.py` 统一管理，15 分钟内自动刷新，不在 tool 层处理鉴权。

## 6. SCM API 端点基址（参考）

| 分类 | 基址 |
| --- | --- |
| Auth | `https://auth.apps.paloaltonetworks.com` |
| Objects | `https://api.strata.paloaltonetworks.com/config/objects/v1` |
| Security | `https://api.strata.paloaltonetworks.com/config/security/v1` |
| Operations | `https://api.strata.paloaltonetworks.com/config/operations/v1` |
| IAM | `https://api.strata.paloaltonetworks.com/iam/v1` |

## 7. OpenAPI 规范来源

位于 `../pan.dev/openapi-specs/scm/`（本仓库外），子目录：
- `auth/AuthService.yaml`
- `config/sase/objects/objects-june.yaml`
- `config/sase/security/security-services-R2-2026.yaml`
- `config/sase/operations/config-operations-march.yaml`
- `iam/ServiceAccounts.yaml`, `iam/Roles.yaml`, `iam/AccessPolicies.yaml`
