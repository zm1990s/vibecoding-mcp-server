# scm-mcp-server

把 **Palo Alto Networks Strata Cloud Manager（SCM）** 的 REST API 封装成 MCP tools，供 Claude Desktop / Cursor / Claude Code 等 MCP 客户端调用。

- 语言：Python 3.10+ · MCP：官方 `mcp` SDK · 传输：stdio · HTTP：`httpx`
- 鉴权：OAuth2 client_credentials，自动刷新 15 分钟令牌
- 设计原则：所有 tool 只转调 SCM REST，不重写业务逻辑；schema 以 openapi-specs/scm 为唯一权威来源
- 详见 `CLAUDE.md`（工程契约）、`DESIGN.md`（工具设计）

## 前置条件

- **Python 3.10+**
- **SCM 服务账号**：在 SCM 控制台 → IAM → Service Accounts 创建，获取 Client ID 和 Client Secret
- **TSG ID**：在 SCM 控制台 → Tenant Service Groups 中查看
- **一个 MCP 客户端**：Claude Desktop / Cursor / Claude Code

## 安装

```bash
git clone <this-repo>
cd vibecoding-mcp-server
pip install -e .
```

## 配置

复制 `.env.example` 为 `.env`，填入真实凭据：

```bash
cp .env.example .env
# 编辑 .env，填入 SCM_CLIENT_ID / SCM_CLIENT_SECRET / SCM_TSG_ID
```

环境变量说明：

| 变量 | 必填 | 说明 |
| --- | --- | --- |
| `SCM_CLIENT_ID` | ✅ | SCM 服务账号 Client ID |
| `SCM_CLIENT_SECRET` | ✅ | SCM 服务账号 Client Secret |
| `SCM_TSG_ID` | ✅ | Tenant Service Group ID |
| `SCM_BASE_URL` | 可选 | 默认 `https://api.strata.paloaltonetworks.com` |
| `SCM_AUTH_URL` | 可选 | 默认 `https://auth.apps.paloaltonetworks.com` |

## 连通性自检

```bash
export SCM_CLIENT_ID=xxx SCM_CLIENT_SECRET=yyy SCM_TSG_ID=zzz
python -m scm_mcp.check
# OK: SCM API 连通（base=https://api.strata.paloaltonetworks.com, tsg_id=zzz）
```

## 注册到 Claude Desktop

在 `~/Library/Application Support/Claude/claude_desktop_config.json` 中添加：

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

## 注册到 Claude Code

```bash
claude mcp add scm python -- -m scm_mcp.server
# 或通过 /mcp 命令在对话中添加
```

设置环境变量后重启客户端即可使用。

## 可用 Tools（37 个）

### Objects（地址/服务/标签等对象）
| Tool | 说明 |
| --- | --- |
| `list_addresses` | 列出地址对象，支持 folder/name 过滤 |
| `create_address` | 创建地址对象（ip-netmask/fqdn 等） |
| `get_address` | 按 UUID 获取地址对象 |
| `update_address` | 更新地址对象 |
| `delete_address` | 删除地址对象 |
| `list_address_groups` | 列出地址组 |
| `create_address_group` | 创建地址组（静态/动态） |
| `get_address_group` | 按 UUID 获取地址组 |
| `update_address_group` | 更新地址组 |
| `delete_address_group` | 删除地址组 |
| `list_services` | 列出服务对象 |
| `create_service` | 创建服务对象 |
| `list_service_groups` | 列出服务组 |
| `create_service_group` | 创建服务组 |
| `list_tags` | 列出标签 |
| `create_tag` | 创建标签 |
| `list_application_groups` | 列出应用组 |
| `list_external_dynamic_lists` | 列出外部动态列表（EDL） |

### Security（安全策略与配置文件）
| Tool | 说明 |
| --- | --- |
| `list_security_rules` | 列出安全策略规则 |
| `create_security_rule` | 创建安全策略规则 |
| `get_security_rule` | 按 UUID 获取安全规则 |
| `update_security_rule` | 更新安全规则 |
| `delete_security_rule` | 删除安全规则 |
| `list_anti_spyware_profiles` | 列出反间谍软件配置文件 |
| `list_vulnerability_profiles` | 列出漏洞防护配置文件 |
| `list_wildfire_profiles` | 列出 WildFire 配置文件 |
| `list_dns_security_profiles` | 列出 DNS 安全配置文件 |
| `list_url_categories` | 列出自定义 URL 分类 |
| `list_decryption_rules` | 列出解密规则 |
| `list_decryption_profiles` | 列出解密配置文件 |

### Operations（配置推送与版本）
| Tool | 说明 |
| --- | --- |
| `list_jobs` | 列出配置任务（查看 push 进度） |
| `get_job` | 按 ID 获取 Job 详情 |
| `list_config_versions` | 列出配置版本历史 |
| `push_candidate_config` | 将候选配置推送到指定 folder/设备 |

### IAM（身份与权限）
| Tool | 说明 |
| --- | --- |
| `list_service_accounts` | 列出服务账号 |
| `list_roles` | 列出角色 |
| `list_access_policies` | 列出访问策略 |

## 开发

```bash
pip install -e ".[dev]"
pytest                          # 单测（mock，不需要 SCM 在线）
pytest -m integration           # 集成测试（需要真实 SCM 凭据）
python scripts/smoke_stdio.py   # stdio 协议级冒烟
```
