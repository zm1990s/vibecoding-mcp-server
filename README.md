# scm-mcp-server

把 **Palo Alto Networks Strata Cloud Manager（SCM）** 的 REST API 封装成 MCP tools，供 Claude Desktop / Cursor / Claude Code 等 MCP 客户端通过自然语言调用。

- 语言：Python 3.10+ · MCP：官方 `mcp` SDK · 传输：stdio · HTTP：`httpx`
- 鉴权：OAuth2 client_credentials，自动刷新 15 分钟令牌
- 37 个 tool，覆盖 Objects / Security / Operations / IAM 四个 API 域
- 设计原则：所有 tool 只转调 SCM REST，不重写业务逻辑；schema 以 `openapi-specs/scm` 为唯一权威来源

---

## 前置条件

- **Python 3.10+**
- **SCM 服务账号**：在 SCM 控制台 → IAM → Service Accounts 创建，获取 Client ID 和 Client Secret
- **TSG ID**：在 SCM 控制台 → Tenant Service Groups 中查看
- **一个 MCP 客户端**：Claude Desktop / Cursor / Claude Code 任选其一

---

## 安装

```bash
git clone <this-repo>
cd vibecoding-mcp-server
pip install -e .
```

---

## 配置环境变量

复制示例文件并填入真实凭据：

```bash
cp .env.example .env
# 用编辑器打开 .env，填入下表中的必填项
```

| 变量 | 必填 | 说明 | 默认值 |
|---|---|---|---|
| `SCM_CLIENT_ID` | ✅ | SCM 服务账号 Client ID | — |
| `SCM_CLIENT_SECRET` | ✅ | SCM 服务账号 Client Secret | — |
| `SCM_TSG_ID` | ✅ | Tenant Service Group ID | — |
| `SCM_BASE_URL` | 可选 | SCM API 基址 | `https://api.strata.paloaltonetworks.com` |
| `SCM_AUTH_URL` | 可选 | OAuth2 认证地址 | `https://auth.apps.paloaltonetworks.com` |

---

## 连通性自检

配置好环境变量后，先跑一次自检确认凭据有效：

```bash
export SCM_CLIENT_ID=xxx SCM_CLIENT_SECRET=yyy SCM_TSG_ID=zzz
python -m scm_mcp.check
# 期望输出：OK: SCM API 连通（base=https://api.strata.paloaltonetworks.com, tsg_id=zzz）
```

---

## 注册到 Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`，在 `mcpServers` 下添加：

```json
{
  "mcpServers": {
    "scm": {
      "command": "python",
      "args": ["-m", "scm_mcp.server"],
      "env": {
        "SCM_CLIENT_ID": "your-client-id",
        "SCM_CLIENT_SECRET": "your-client-secret",
        "SCM_TSG_ID": "your-tsg-id"
      }
    }
  }
}
```

保存后重启 Claude Desktop，在对话框左下角可见 MCP 工具图标。

---

## 注册到 Claude Code

```bash
# 添加 MCP server
claude mcp add scm python -- -m scm_mcp.server

# 设置环境变量（在 shell profile 或项目 .env 中）
export SCM_CLIENT_ID=your-client-id
export SCM_CLIENT_SECRET=your-client-secret
export SCM_TSG_ID=your-tsg-id
```

在 Claude Code 对话中输入 `/mcp` 可查看已注册的 server 状态。

---

## 注册到 Cursor

在 Cursor 设置 → MCP → Add Server 中填入：

```json
{
  "name": "scm",
  "command": "python",
  "args": ["-m", "scm_mcp.server"],
  "env": {
    "SCM_CLIENT_ID": "your-client-id",
    "SCM_CLIENT_SECRET": "your-client-secret",
    "SCM_TSG_ID": "your-tsg-id"
  }
}
```

---

## 可用工具一览

| 域 | 工具数 | 代表工具 |
|---|---|---|
| Objects | 18 | `list_addresses`, `create_address`, `list_tags` ... |
| Security | 12 | `list_security_rules`, `create_security_rule` ... |
| Operations | 4 | `list_jobs`, `push_candidate_config` ... |
| IAM | 3 | `list_service_accounts`, `list_roles` ... |

完整映射见 `DESIGN.md §3`。
