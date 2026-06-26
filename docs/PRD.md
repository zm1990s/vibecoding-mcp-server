# PRD — scm-mcp-server（MVP）

> 服从 `CLAUDE.md`（L1）。本文件是产品需求层，只描述「为谁、解决什么、边界、怎么验收」。
> 具体 REST 端点清单 → 以 `../pan.dev/openapi-specs/scm/` 下的 YAML 为准，本文件**不列举、不臆造端点**。
> 技术性的 tool ↔ REST 端点映射 → 见 `DESIGN.md`，本文件只引用、不重画。

## 1. 目标用户与核心场景

| 角色 | 关心什么 | 核心场景 |
| --- | --- | --- |
| **网络安全工程师** | 策略审计、合规检查 | 在 Claude/Cursor 里用自然语言查询某 folder 下的安全规则、地址对象，判断策略覆盖是否符合预期 |
| **平台运维** | 配置变更管理 | 推送候选配置前，先列出当前 config-versions / jobs，确认无冲突任务后再执行 push |
| **安全架构师** | 设计评审 | 快速检索现有 Anti-Spyware / Vulnerability Protection profiles，评估防护层是否完整 |
| **IAM 管理员** | 权限审计 | 列出服务账号、角色与访问策略，核查最小权限原则落实情况 |

共同点：**不切换工具**，直接在 MCP 客户端（Claude Desktop / Cursor / Claude Code）里通过对话调用 SCM REST 能力。

## 2. MVP 功能边界

### In Scope（MVP 必须具备的能力）

- **C1 对象查询**：查询地址对象、地址组、服务对象、服务组、标签、应用组、外部动态列表（EDL）。
- **C2 安全策略查询**：查询安全规则、安全配置文件（Anti-Spyware / Vulnerability / WildFire / DNS / URL / Decryption）。
- **C3 配置操作**：查询配置 Jobs / 版本历史；将候选配置推送到目标 folder 或设备。
- **C4 对象写操作**：创建/更新/删除地址对象、地址组、服务对象、服务组、标签；创建/更新/删除安全规则。
- **C5 IAM 查询**：查询服务账号、角色、访问策略。
- **C6 环境可切换**：通过 `SCM_BASE_URL` 指向不同 SCM 实例，能力不变。

> 上述能力**仅在 openapi-specs 中有对应端点时**才落地为 tool；规范未提供的能力本 MVP 不自造。

### Out of Scope（MVP 明确不做）

- ❌ 不重写 SCM 业务逻辑（策略计算、流量分析、报告生成等一律调 REST）。
- ❌ 不在 tool 层处理 token 刷新以外的鉴权逻辑（IAM 由 SCM 侧控制）。
- ❌ 不做前端 UI、可视化图表。
- ❌ 不做跨 tenant 数据合并、缓存、长期持久化。
- ❌ 不新增除 stdio 外的传输方式。
- ❌ 不暴露 Auth API 为 tool（OAuth2 token 获取由 `auth.py` 内部处理）。
- ❌ SASE deployment / mobile agent / network services 等高复杂度写操作（后续批次评估）。

## 3. 产品级数据流

```
用户（自然语言）
   │  在 Claude / Cursor 中提问
   ▼
MCP 客户端  ──选择 tool──►  scm-mcp-server (stdio)
                                  │  自动获取/刷新 Bearer token
                                  │  组装请求（不加业务逻辑）
                                  ▼
                        SCM REST API（api.strata.paloaltonetworks.com）
                                  │  SCM 执行查询/配置变更
                                  ▼
                        响应 ──透传──► MCP 客户端 ──► 用户看到结果
```

- 用户用「能力」（§2 的 C1–C5），不需要知道端点或 token。
- 「能力 → 具体 tool → REST 端点」的映射是技术细节，**见 `DESIGN.md`**，此处不重画。
- MCP server 在链路中只做"刷 token → 组装请求 → 调 REST → 透传"，不做业务计算。

## 4. 验收标准（可观察 / 可验证）

| # | 标准 | 验证方式 |
| --- | --- | --- |
| A1 | 每个 MVP 能力（C1–C5）至少对应 1 个可在 `tools/list` 中列出的 tool | 启动后执行 `tools/list`，逐能力核对存在对应 tool |
| A2 | 调用任一只读 tool，返回的字段与 openapi-specs 中该端点的 response schema 一致（无多余/臆造字段） | 对比 tool 返回结构与 YAML 定义 |
| A3 | 写操作 tool 执行后，SCM 控制台中可观察到对应变更 | 执行 `create_address`，在 SCM UI 中确认对象出现 |
| A4 | 修改 `SCM_BASE_URL` 后，请求目标地址随之改变，且无需改动代码 | 改环境变量后抓包确认目标 host 变化 |
| A5 | token 自动刷新：连续运行超过 15 分钟后，tool 调用仍然成功 | 等待 15+ 分钟后调用只读 tool，无 401 报错 |
| A6 | REST 返回非 2xx 时，tool 返回含 status code + 响应体的结构化错误，不静默吞错 | 构造一个失败请求（如无效 UUID），观察 tool 返回内容 |
| A7 | openapi-specs 未暴露的能力不存在对应 tool | 比对 `tools/list` 与 YAML paths，无多出的 tool |

> 验收文案禁用"流畅""好用""快"等主观词；每条均为可执行的二元判定。

## 5. 风险与待确认问题

| # | 类型 | 描述 | 待确认 |
| --- | --- | --- | --- |
| R1 | 凭据安全 | SCM_CLIENT_SECRET 在环境变量中明文传递给 MCP server | 部署环境是否有 secret manager？是否接受明文 env？ |
| R2 | 写操作防误触 | `create_security_rule` / `push_candidate_config` 等写操作无二次确认机制 | 是否需要在 tool description 中强化 ⚠️ 警示？客户端是否有操作确认流程？ |
| R3 | Token 权限边界 | Service account 的权限决定哪些 API 可调用，权限不足时返回 403 | 所需的最小 SCM 角色/权限集合需与平台管理员确认 |
| R4 | 分页完整性 | 默认 limit=200，超大规模 folder 可能返回不完整数据 | 是否需要自动分页聚合？（当前 Out of Scope，需确认风险接受度） |
| R5 | 数据敏感性 | SCM 策略配置可能含有内网 IP、应用名等敏感信息，经 MCP 客户端处理 | 是否有数据出境/合规限制？ |
| R6 | API 版本漂移 | SCM API 版本升级时，openapi-specs YAML 需同步更新 | 是否有自动化机制感知 API 变更？ |
