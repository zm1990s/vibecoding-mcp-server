# PRD — scm-mcp-server（MVP）

> 服从 `CLAUDE.md`（L1）。本文件是产品需求层，只描述「为谁、解决什么、边界、怎么验收」。
> 具体 REST 端点清单 → 以 `../pan.dev/openapi-specs/scm/` 下的 YAML 为准，本文件**不列举、不臆造端点**。
> 技术性的 tool ↔ REST 端点映射 → 见 `DESIGN.md`，本文件只引用、不重画。

---

## 1. 目标用户与核心场景

### 1.1 网络安全工程师

**关心什么**：策略正确性、合规覆盖、规则审计。

**典型场景**：
- 在 Claude 里输入「列出 Global folder 下所有允许 any-any 的安全规则」，直接得到结构化列表，判断是否违反最小权限原则，无需登录 SCM 控制台手动翻页。
- 输入「这条规则的 action 是什么」，MCP server 返回规则对象，工程师直接在对话中决策是否需要修改。

### 1.2 平台运维

**关心什么**：变更窗口管理、配置推送前置检查、任务状态跟踪。

**典型场景**：
- 变更前输入「当前有没有正在运行的 push job」，确认无冲突任务后再执行推送，全程在同一对话窗口完成，不需要切换工具。
- 推送后输入「刚才那个 job 完成了吗」，MCP server 查询 job 状态并透传结果。

### 1.3 安全架构师

**关心什么**：防护层完整性、配置文件覆盖情况、设计评审效率。

**典型场景**：
- 输入「列出所有 Anti-Spyware 和 Vulnerability Protection profile」，快速核查防护配置文件是否齐备，评估哪些规则尚未挂载安全配置文件。
- 设计评审会议中，直接从 Claude 拉取当前策略配置作为基线数据，不需要提前导出报表。

### 1.4 IAM 管理员

**关心什么**：最小权限落实、服务账号清单、访问策略合规。

**典型场景**：
- 输入「列出所有服务账号及其绑定的角色」，核查是否有过期或权限过宽的账号，全程不需要登录 IAM 控制台。
- 输入「现有访问策略里有没有绑定超级管理员角色的条目」，MCP server 返回原始策略列表，管理员自行判断风险。

---

## 2. MVP 功能边界

### 2.1 In Scope（MVP 必须具备的能力）

以下能力描述以 `DESIGN.md §3` 为实现基础，具体端点以 `openapi-specs/scm/` YAML 为准，本文件不列举端点、不臆造字段。

| 能力 ID | 能力描述 | 包含操作类型 |
|---|---|---|
| **C1 对象管理** | 查询和写入地址对象、地址组、服务对象、服务组、标签、应用组、外部动态列表（EDL） | 只读 + ⚠️ 写操作 |
| **C2 安全策略管理** | 查询和写入安全规则；查询安全配置文件（反间谍、漏洞防护、WildFire、DNS 安全、URL 分类、解密规则与配置文件） | 只读 + ⚠️ 写操作 |
| **C3 配置运维** | 查询 Job 状态与配置版本历史；将候选配置推送到目标 folder 或设备 | 只读 + ⚠️ 写操作 |
| **C4 IAM 查询** | 查询服务账号、角色、访问策略 | 只读 |
| **C5 环境可切换** | 通过 `SCM_BASE_URL` 环境变量指向不同 SCM 实例，能力不变，无需改代码 | 配置项 |

> 上述能力**仅在 `openapi-specs/scm/` YAML 中有对应端点时**才落地为 tool；规范未提供的能力本 MVP 不自造。

### 2.2 Out of Scope（MVP 明确不做，附排除理由）

| 排除项 | 理由 |
|---|---|
| Auth API 暴露为 tool | OAuth2 token 获取是内部基础设施，不是用户能力；由 `auth.py` 内部处理 |
| SASE Deployment / Mobile Agent / Network Services 写操作 | 端点复杂度高、误操作影响面大，需专项评估后再纳入 |
| NGFW / Cloud NGFW 专属端点 | SASE 场景优先；NGFW 场景后续批次单独评估 |
| 跨 tenant 数据合并与缓存 | 超出单次 REST 调用的范围，引入状态复杂度 |
| 自动分页聚合 | 超大规模 folder 的完整性风险已在 §5 列为待确认项，当前不自动处理 |
| 前端 UI / 可视化 | MCP 客户端（Claude / Cursor）承担交互层，server 不做额外渲染 |
| HTTP/SSE/WebSocket 传输 | 只 stdio，见 `CLAUDE.md §2` |

---

## 3. 产品级数据流

```
用户（自然语言提问）
    │
    │  在 Claude Desktop / Cursor / Claude Code 中输入
    ▼
MCP 客户端
    │  识别意图 → 选择对应 tool → 传入参数
    ▼
scm-mcp-server（stdio 进程）
    │  1. auth.py：检查 token 是否有效，过期则自动刷新
    │  2. 组装 HTTP 请求（不加业务逻辑）
    │  3. httpx 发出请求
    ▼
SCM REST API（api.strata.paloaltonetworks.com）
    │  执行查询或配置变更
    ▼
HTTP 响应
    │  2xx → 原样透传
    │  非 2xx → 结构化为 {error, status, body} 后透传
    ▼
MCP 客户端 → 用户看到结果
```

**关键约束**：
- server 在链路中只做「刷 token → 组装请求 → 调 REST → 透传」，不做业务计算、不缓存数据、不改写响应结构。
- token 刷新发生在 server 内部，用户和 MCP 客户端对此无感。
- **能力 → 具体 tool → REST 端点** 的映射是技术实现细节，见 `DESIGN.md §3`，本文件不重复。

---

## 4. 验收标准

每条均为可执行的二元判定，禁用「流畅」「好用」「快速」等主观词。

| # | 验收项 | 验证方式 | 通过标准 |
|---|---|---|---|
| A1 | MVP 能力覆盖 | 启动 server 后执行 `tools/list`，逐能力（C1–C4）核对 | 每个能力至少有 1 个 tool 出现在列表中 |
| A2 | 只读 tool 字段合规 | 调用任一只读 tool，对比返回字段与 `openapi-specs` 中该端点的 response schema | 无多余字段、无臆造字段，与 YAML 定义一致 |
| A3 | 写操作可验证 | 执行任一写 tool（如创建地址对象），到 SCM 控制台核查 | SCM 控制台中对应对象出现（或变更生效） |
| A4 | 环境变量切换生效 | 修改 `SCM_BASE_URL`，重启 server 后发起请求，抓包或查看日志 | 请求目标 host 变为新值，无需改代码 |
| A5 | token 自动刷新 | 连续运行超过 15 分钟后调用只读 tool | 返回正常响应，无 401 错误 |
| A6 | 非 2xx 结构化错误 | 构造一个失败请求（如传入无效 UUID） | tool 返回包含 `error: true`、`status`（HTTP 状态码）、`body`（原始响应体）的 JSON 对象 |
| A7 | 无超出规范的 tool | 对比 `tools/list` 输出与 `openapi-specs` YAML 中的 paths | `tools/list` 中无任何在 YAML 中找不到对应端点的 tool |

---

## 5. 风险与待确认问题

### R1 凭据安全

**风险**：`SCM_CLIENT_SECRET` 以明文环境变量传入 MCP server 进程，存在泄漏路径（shell history、进程列表、`.env` 文件误入版本库）。

**当前缓解**：`.env` 已在 `.gitignore` 中排除；stdio 传输限制了网络暴露面；凭据不在代码中硬编码。

**待确认**：
- 部署环境是否有 secret manager（如 macOS Keychain、Vault、AWS Secrets Manager）可替代明文 env？
- 是否接受当前明文 env 方案，或需要在 README 中强制加警告？

---

### R2 写操作防误触

**风险**：`create_security_rule`、`push_candidate_config`、`delete_address` 等写操作无二次确认机制。LLM 在理解用户意图时可能主动触发写 tool，导致非预期的 SCM 配置变更。

**当前缓解**：写操作 tool 的 description 中标注「⚠️ 写操作」；tool 参数需用户（或 LLM）主动提供，不能零参数触发。

**待确认**：
- 是否需要在 tool description 中增加更强的警示文案（如「执行前请确认 folder 和对象名称」）？
- 目标 MCP 客户端（Claude Desktop / Cursor）是否有操作确认弹窗机制可利用？
- 是否需要在 MVP 阶段将高风险写操作（如 `push_candidate_config`、`delete_*`）默认禁用，改为显式 opt-in？

---

### R3 Token 权限边界

**风险**：`auth.py` 用 client_credentials 获取 token，token 的实际权限由 SCM 服务账号配置决定。MCP server 不做额外的权限限制，服务账号权限过宽时，server 暴露的能力也会过宽。

**当前缓解**：server 只暴露 DESIGN.md 中定义的 37 个 tool，不暴露全量 SCM API；权限边界由 SCM IAM 侧控制。

**待确认**：
- 不同角色（只读审计 vs 运维写操作）是否需要使用不同服务账号？
- 是否需要在 README 中提供最小权限服务账号配置建议？

---

### R4 API 版本漂移

**风险**：`openapi-specs/scm/` YAML 文件是静态快照。SCM 线上 API 升级（字段变更、端点废弃、新增必填参数）时，server 行为与实际 API 不一致，可能导致静默错误或运行时失败。

**当前缓解**：非 2xx 响应统一结构化透传，字段变更会在 tool 返回中反映；`WORKFLOW.md` 定义了「API 变更 → 先同步 YAML → 再改代码」的漂移处理流程。

**待确认**：
- 是否有自动化机制（如 CI 中定期拉取最新 YAML 并做 diff）感知 API 变更？
- SCM 是否提供 API 变更 changelog 订阅渠道？
