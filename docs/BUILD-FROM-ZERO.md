# 从 0 构建：scm-mcp-server 构建手册

> 记录如何从零搭建这个 SCM MCP server 的完整过程。
> 配合 git branch `scm` 使用。

---

## 1. 总览

### 这是什么

一个 **MCP server**：把 Palo Alto Networks Strata Cloud Manager（SCM）已有的 REST API，封装成一组 MCP tools，供 Claude Desktop / Cursor 等 MCP 客户端通过自然语言调用。它**不是**新平台——只做「刷 token → 组装请求 → 调 SCM REST → 透传响应」。

### 最终成果

- **37 个 tool**，覆盖 Objects / Security / Operations / IAM 四个 API 域。
- 语法检查：7 个源文件全部 `ast.parse` 通过。
- 路由完整性：37 个 tool 全部有对应路由条目。

### 技术栈（钉死，引 `CLAUDE.md` §2）

| 项 | 选定 |
| --- | --- |
| 语言 | Python 3.10+ |
| MCP | 官方 `mcp` SDK |
| 传输 | stdio（唯一） |
| HTTP | `httpx` |
| 鉴权 | OAuth2 client_credentials（`auth.py` 自动管理） |

### 贯穿全程的四条红线（引 `CLAUDE.md` §4）

1. schema 唯一权威来源是 `openapi-specs/scm/` YAML，不手抄、不臆造。
2. 只转调 REST，不重写 SCM 业务逻辑。
3. 不硬编码地址与凭据，走环境变量。
4. 只用 stdio。

### 分层文档（Context Stack）

- **L1 `CLAUDE.md`**：工程契约（技术栈/红线/目录）。
- **L2 `DESIGN.md`**：tool ↔ REST 端点映射表（37 条）。
- **L3 `WORKFLOW.md`**：阶段协议（阶段 1 契约同步 → 2 实现 → 3 验收）+ 验收记录。
- `docs/PRD.md`：产品需求。`README.md`：怎么跑/怎么注册。

---

## 2. 从零构建步骤

### Step 0 — 准备 SCM 凭据

在 SCM 控制台完成以下操作：

1. **IAM → Service Accounts** → 创建服务账号，获取 Client ID 和 Client Secret。
2. **Tenant Service Groups** → 记录 TSG ID。
3. 为服务账号分配所需角色（建议：`Security Admin` 用于策略读写；只读场景用 `Viewer`）。

将凭据写入 `.env`（复制 `.env.example`）：

```bash
cp .env.example .env
# 填入 SCM_CLIENT_ID / SCM_CLIENT_SECRET / SCM_TSG_ID
```

### Step 1 — 建立 Context Stack 契约

先立文档结构再写代码，四层文件一次性到位：

```
CLAUDE.md    # L1：技术栈钉死、禁止事项、必须执行
DESIGN.md    # L2：tool ↔ REST 端点映射表（引用 openapi-specs YAML）
WORKFLOW.md  # L3：阶段协议 + 验收记录
README.md    # 用户文档
docs/PRD.md  # 产品需求
```

**教学点**：先立**契约**再写任何代码。L1 钉死不可变项，下层服从上层。DESIGN 映射表按 openapi-specs YAML 填充，不臆造。

### Step 2 — 阅读 OpenAPI 规范

在 `../pan.dev/openapi-specs/scm/` 下阅读以下关键文件，提取需要暴露的端点：

| 文件 | API 域 | 基址 |
| --- | --- | --- |
| `auth/AuthService.yaml` | Auth（内部用） | `https://auth.apps.paloaltonetworks.com` |
| `config/sase/objects/objects-june.yaml` | Objects | `/config/objects/v1` |
| `config/sase/security/security-services-R2-2026.yaml` | Security | `/config/security/v1` |
| `config/sase/operations/config-operations-march.yaml` | Operations | `/config/operations/v1` |
| `iam/ServiceAccounts.yaml` 等 | IAM | `/iam/v1` |

**提取原则**：

- 每个 `(path, method)` 对 → 一个 tool。
- 命名：`{动作}_{资源}`，小写下划线。`GET /addresses` → `list_addresses`，`POST /addresses` → `create_address`。
- 写操作（POST/PUT/DELETE）在 description 标注 `⚠️ 写操作`。
- Auth token 端点不暴露（由 `auth.py` 内部处理）。

### Step 3 — 搭项目骨架

```bash
mkdir -p src/scm_mcp
touch src/scm_mcp/__init__.py
pip install mcp httpx
```

目录结构：

```
src/scm_mcp/
├── __init__.py    # 版本号
├── config.py      # 环境变量读取
├── auth.py        # OAuth2 token 管理
├── rest_client.py # REST 薄封装
├── tools.py       # 37 个 tool 定义与路由
├── server.py      # MCP stdio server 入口
└── check.py       # 连通性自检
```

### Step 4 — 实现 OAuth2 鉴权（`auth.py`）

SCM 使用 OAuth2 client_credentials 流程，access token 有效期 15 分钟。

关键设计：

- **缓存 + 自动刷新**：用 `time.monotonic()` 记录过期时间，提前 60s 刷新。
- **线程安全**：`threading.Lock` 保护全局 token 缓存，适配 server.py 中的 `asyncio.to_thread` 调用。

```python
# 核心逻辑（简化）
if _token is None or time.monotonic() >= _expires_at:
    _token, _expires_at = _fetch_token()   # 调 /auth/v1/oauth2/access_token
return _token
```

### Step 5 — 实现 REST 客户端（`rest_client.py`）

职责极简：注入 Bearer token + 发请求 + 返回 (status, body)。

```python
def request(method, full_path, *, params=None, json=None):
    url = config.get_base_url() + full_path
    headers = auth.bearer_headers()          # 自动刷新
    resp = httpx.Client().request(method, url, headers=headers, params=params, json=json)
    return resp.status_code, _body(resp)     # 不抛非 2xx
```

### Step 6 — 实现 Tools（`tools.py`）

37 个 tool 用**路由表驱动**，避免大量重复代码。四张路由表：

```python
_LIST_TOOLS   = {"list_addresses": ("/config/objects/v1/addresses", ("name", "folder", ...)), ...}
_GET_BY_ID_TOOLS = {"get_address": "/config/objects/v1/addresses", ...}
_DELETE_TOOLS    = {"delete_address": "/config/objects/v1/addresses", ...}
_CREATE_TOOLS    = {"create_address": ("/config/objects/v1/addresses", container_keys, body_keys), ...}
_UPDATE_TOOLS    = {"update_address": ("/config/objects/v1/addresses", body_keys), ...}
# 特殊处理：push_candidate_config（直接在 call() 里写）
```

`call()` 函数按路由表分发，每类只有 3-5 行逻辑。

**路由完整性验证**：

```python
routed = set(_LIST_TOOLS) | set(_GET_BY_ID_TOOLS) | set(_DELETE_TOOLS) | set(_CREATE_TOOLS) | set(_UPDATE_TOOLS) | {"push_candidate_config"}
assert {t.name for t in TOOLS} == routed  # 无遗漏
```

### Step 7 — 连通性自检

```bash
export SCM_CLIENT_ID=xxx SCM_CLIENT_SECRET=yyy SCM_TSG_ID=zzz
python -m scm_mcp.check
# OK: SCM API 连通（base=https://api.strata.paloaltonetworks.com, tsg_id=zzz）
#     token=eyJhbGci...  /config/operations/v1/jobs -> HTTP 200
```

### Step 8 — stdio 冒烟测试

```bash
python scripts/smoke_stdio.py
# [1] initialize: OK
# [2] tools/list: 37 tools
#     OK: all 37 expected tools present
# [3] call_tool(list_jobs): {"data": [...], "total": ...}
# SMOKE OK
```

---

## 3. 常见问题

| 问题 | 原因 | 解决 |
| --- | --- | --- |
| `RuntimeError: 环境变量 SCM_CLIENT_ID 未设置` | 未配置凭据 | 检查 `.env` 或环境变量是否正确导出 |
| `HTTP 401` | token 无效或 TSG_ID 不匹配 | 确认 CLIENT_SECRET 正确；确认 TSG_ID 是服务账号有权限的 TSG |
| `HTTP 403` | 服务账号权限不足 | 在 SCM → IAM 为服务账号分配更高权限角色 |
| `HTTP 400` on list | folder/snippet/device 参数缺失 | SCM 列表 API 要求至少提供一个容器参数（folder/snippet/device） |
| tool 在 MCP 客户端不出现 | 会话未重启 | 关闭重开会话；确认 `scm-mcp` 已在 MCP 配置中注册 |

---

## 4. 扩展：新增 Tool 的流程

1. **阶段 1**：在 `openapi-specs/scm/` 对应 YAML 中找到目标端点，记录路径/方法/参数/响应。
2. **阶段 2**：
   - 在 `DESIGN.md` 对应小节追加一行映射。
   - 在 `tools.py` 的 `TOOLS` 列表中追加 `types.Tool(...)` 定义。
   - 将新 tool 名加入对应路由表（`_LIST_TOOLS` / `_CREATE_TOOLS` 等）。
3. **阶段 3**：运行语法检查 + 路由完整性验证 + smoke_stdio.py。
