# 从 0 跟做：scm-mcp-server 构建手册

> 给想从头复现这个项目的人的「逐步轨迹」手册。
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

## 2. 逐步轨迹

> 每节：**真实提示词（逐字，可直接复制）** → 关键决策/教学点 → 验收 → **commit / tag / push**。
> ⚠️ 下面的提示词是构建时**原样使用**的——红线约束、⚠️ 副作用提醒、"先给计划我确认"的 gating 一字未删。
> 照抄即可复现同样的轨迹；删掉这些约束，复现质量会下降。

### Git 提交规范（每步必做）

> **每完成一个 Step，必须执行以下三步后再继续下一步。轨迹不落盘，复现就会断。**

```bash
# 1. 提交（message 格式：step-N: 一句话描述）
git add -A
git commit -m "step-N: <本步描述>"

# 2. 打 tag（轻量 tag，名称与 step 号对应）
git tag step-N

# 3. 推送 commit 和 tag
git push origin scm
git push origin step-N
```

Tag 命名约定：

| Step | Tag | 描述 |
|---|---|---|
| Step 0 | `step-0` | Context Stack 契约 |
| Step 1 | `step-1` | PRD |
| Step 2 | `step-2` | 项目骨架 |
| Step 3 | `step-3` | DESIGN 映射表填充 |
| Step 4a | `step-4a` | Objects 只读 tools |
| Step 4b | `step-4b` | Objects 写操作 tools |
| Step 5 | `step-5` | Security / Operations / IAM tools |
| Step 6 | `step-6` | 阶段 3 收口 + 冒烟 |

检出任意历史节点：`git checkout step-N`

---

### Step 0 — Context Stack 契约

**真实提示词（逐字）**：

```
你是架构助手。我要给 Palo Alto Networks Strata Cloud Manager（SCM）写一个 MCP server。

要求：先不要输出任何代码，只输出计划（要建哪些文件、每个文件写什么）；我确认后你再生成；最后告诉我怎么验收。

要建的文件（对应 Context Stack 分层）：
a. CLAUDE.md — L1 工程契约（项目身份、技术栈不要换、目录约定、禁止事项、必须执行）
b. DESIGN.md — L2 设计（暴露哪些 MCP tool，各自包哪个 REST 端点，入参/出参）
c. WORKFLOW.md — L3 阶段协议
d. README.md — 给人看：怎么跑、怎么在 Claude/Cursor 里注册

技术栈（请在 CLAUDE.md 钉死）：Python，官方 mcp SDK，stdio 传输，httpx HTTP 客户端。

关键约束：
- tool 的入参/出参 schema 唯一来源是 openapi-specs/scm/ 下的 YAML 文件，不要手抄、不要臆造。
- 只通过 REST 调用 SCM，不重写业务逻辑。
- SCM 使用 OAuth2 client_credentials，凭据走环境变量 SCM_CLIENT_ID / SCM_CLIENT_SECRET / SCM_TSG_ID。
- SCM API 基址走环境变量 SCM_BASE_URL，默认 https://api.strata.paloaltonetworks.com，不硬编码。

OpenAPI 规范位于本仓库同级目录 ../pan.dev/openapi-specs/scm/，子目录包含 auth/、config/（sase/ngfw/cloudngfw 等）、iam/ 等分类。
```

**教学点**：先立**契约**再写任何代码。L1 钉死不可变项，下层服从上层。DESIGN 映射表此时是空骨架——**故意的**，留给阶段 1 用 openapi-specs YAML 填。与日志分析版的关键区别：SCM 需要 OAuth2（auth.py 单独成文件），这是 L1 就要钉死的架构决策。

**验收**：4 文件齐、红线可读、OAuth2 凭据读取方式明确。

**提交**：
```bash
git add -A && git commit -m "step-0: 建立 Context Stack 契约（CLAUDE/DESIGN/WORKFLOW/README）"
git tag step-0 && git push origin scm && git push origin step-0
```

---

### Step 1 — PRD

**真实提示词（逐字）**：

```
基于 CLAUDE.md，你现在是产品与架构助手。请不要写代码。

先输出计划，再生成 docs/PRD.md，内容包含：
1. 目标用户与核心场景（网络安全工程师 / 平台运维 / 安全架构师 / IAM 管理员）
2. MVP 功能边界（明确 in scope / out of scope）。用能力描述，具体端点清单以 openapi-specs/scm/ YAML 为准，本文件不列举/不臆造端点。
3. 产品级数据流（用户 → MCP → SCM REST → 结果）。技术性的 tool↔REST 端点映射属于 DESIGN.md，本文件只引用、不重画。
4. 验收标准（每条可观察、可验证，禁用"流畅"等主观词）。
5. 风险与待确认问题（重点关注：凭据安全、写操作防误触、token 权限边界、API 版本漂移）。

另外：把 docs/PRD.md 补进 CLAUDE.md 第 3 节目录约定，保持 L1 自洽。
```

**教学点**：PRD 写**能力**不写端点——端点是 L2 的事，避免跨层重复与臆造。验收标准必须二元可判定。SCM 是生产系统，PRD 里要显式标注写操作风险（误触配置推送等）。

**验收**：验收标准 A1–A7 每条可执行；PRD 不含端点清单；风险表含凭据和写操作条目。

**提交**：
```bash
git add -A && git commit -m "step-1: 新增 docs/PRD.md，更新 CLAUDE.md 目录约定"
git tag step-1 && git push origin scm && git push origin step-1
```

---

### Step 2 — 项目骨架

**真实提示词（逐字）**：

```
基于 docs/PRD.md、DESIGN.md 和 CLAUDE.md 的目录约定，生成项目骨架（仅结构，不含具体业务 tool）。

先列完整目录树让我确认，再生成关键文件，最后给可执行的验收命令。

骨架范围（务必遵守）：
- 产出：目录结构、pyproject.toml、.env.example（含 SCM_CLIENT_ID/SCM_CLIENT_SECRET/SCM_TSG_ID/SCM_BASE_URL）、以下 5 个模块骨架：
  - config.py：读取 5 个 SCM 环境变量（BASE_URL/AUTH_URL/CLIENT_ID/SECRET/TSG_ID），缺必填项时 raise RuntimeError
  - auth.py：OAuth2 client_credentials 骨架（_fetch_token 调 /auth/v1/oauth2/access_token，get_token 做缓存+刷新，bearer_headers 返回 headers 字典）；token 有效期 15 分钟，提前 60s 刷新，threading.Lock 保证线程安全
  - rest_client.py：request(method, full_path, *, params, json) → (status, body)，注入 bearer_headers，不抛非 2xx
  - server.py：官方 mcp SDK + stdio，list_tools 返回空列表（TODO 占位），call_tool 分发到 tools.call
  - check.py：连通性自检（获取 token + 调一次 GET /config/operations/v1/jobs），退出码 0/1
- 不要生成任何具体 tool。tool↔端点映射当前为 _TBD_，其填充是 WORKFLOW.md 阶段 1 的第一步。

验收命令需可实际运行：pip install -e .、python -m scm_mcp.check（配好凭据后）、stdio 启动不报错、tools/list 返回空列表。
```

**教学点**：骨架先于 tool。`auth.py` 独立成模块是 SCM 与日志分析版的最大区别——OAuth2 刷新逻辑有状态（缓存 + 锁），不应混进 rest_client。`check.py` 的自检分两步：先拿 token（验证凭据），再调 API（验证权限），两步分开报错让故障更易定位。

**验收**：`pip install -e .` 通过；`python -m scm_mcp.check` 在凭据正确时输出 `OK`；`tools/list` 返回 `[]`。

**提交**：
```bash
git add -A && git commit -m "step-2: 搭项目骨架（config/auth/rest_client/server/check，tools 空列表占位）"
git tag step-2 && git push origin scm && git push origin step-2
```

---

### Step 3 — 阅读 OpenAPI 规范 + 填写 DESIGN 映射表

**真实提示词（逐字）**：

```
执行 WORKFLOW.md 阶段 1：契约同步。请不要写任何代码。

阅读以下 openapi-specs/scm/ 下的 YAML 文件，提取需要暴露为 MCP tool 的端点，填充 DESIGN.md §3 映射表：
- auth/AuthService.yaml（仅供 auth.py 内部使用，不暴露 tool）
- config/sase/objects/objects-june.yaml
- config/sase/security/security-services-R2-2026.yaml
- config/sase/operations/config-operations-march.yaml
- iam/ServiceAccounts.yaml、iam/Roles.yaml、iam/AccessPolicies.yaml

提取与排除原则：
- 每个 (path, method) → 一个 tool，命名为 {动作}_{资源}（小写下划线）
- 只读 tool 优先；写操作（POST/PUT/DELETE）纳入但在 description 标注「⚠️ 写操作」
- Auth token 端点（/auth/v1/oauth2/*）不暴露，由 auth.py 内部处理
- SASE deployment / mobile agent / network services 等高复杂度写操作暂列为"后续批次"
- 每行记录：tool 名、HTTP 方法+路径、类型（只读/写）、OpenAPI YAML 引用位置
- 映射表填完后，统计 tool 总数，向我确认范围再进入阶段 2

先输出你提取到的端点清单和 tool 命名列表，等我确认后再正式写入 DESIGN.md。
```

**教学点**：阶段 1 不只是"填表"，还包含**范围判断**——不是每个端点都该变成 tool。Auth 端点内部化（不暴露）是核心设计决策。SASE 网络配置类端点参数复杂、不确定性高，先排除、后续再评估，而不是强行全覆盖。

**验收**：DESIGN.md §3 无 `_TBD_`，每行可在对应 YAML 中定位；tool 命名符合 `{动作}_{资源}` 规范。

**提交**：
```bash
git add -A && git commit -m "step-3: 填充 DESIGN.md 映射表（37 个 tool，4 个 API 域）"
git tag step-3 && git push origin scm && git push origin step-3
```

---

### Step 4a — 实现 Objects API tools（只读批）

**真实提示词（逐字）**：

```
执行 WORKFLOW.md 阶段 2：实现。先实现 Objects API 的只读 tool（list_* 和 get_* 类），不含写操作。服从 CLAUDE.md 红线，按 DESIGN §3.1 映射表逐条实现。

先给实现计划（分几步，每步一个 commit），我确认后再逐步做。

约束：
- inputSchema 按 openapi-specs/scm/config/sase/objects/objects-june.yaml 中对应端点的 parameters 填写；folder/snippet/device/name/offset/limit 等公共查询参数用共享常量定义，不在每个 tool 里重复写
- tool 只做「组装请求 → rest_client.request → 透传响应」；非 2xx 按 DESIGN §4 返回 {error, status, body}
- 用路由表驱动（dict 映射 tool 名 → (path, param_keys)），避免重复的 if/elif
- 先搭 pytest 脚手架（mock rest_client.request），再实现 tool，每步跑测试
- 不实现写操作 tool（create_*/update_*/delete_*），留给下一批
```

**教学点**：路由表驱动是本项目最重要的代码设计——37 个 tool 如果每个写一段 if/elif，代码会失控。`_LIST_TOOLS = {name: (path, param_keys)}` 让新增 tool 只需加一行字典条目。list 类 tool 的公共参数（folder/snippet/device/name/offset/limit）提取为常量，openapi 里这些参数在每个端点都重复出现，集中定义避免每个 tool 单独手写。

**验收**：`pytest -q` 通过（mock 层）；`tools/list` 能列出实现的只读 tool；调 `list_addresses`（传 folder 参数）返回 SCM 真实响应。

**提交**：
```bash
git add -A && git commit -m "step-4a: 实现 Objects API 只读 tool（list/get 类，路由表驱动）"
git tag step-4a && git push origin scm && git push origin step-4a
```

---

### Step 4b — 实现 Objects API tools（写操作批）

**真实提示词（逐字）**：

```
继续实现 Objects API 的写操作 tool（create_*/update_*/delete_*），服从 CLAUDE.md 红线。

约束：
- inputSchema 从 objects-june.yaml 中对应端点的 requestBody schema 提取；只填 openapi 明确定义的字段，不臆造
- create_* tool：container 参数（folder/snippet/device）走 query params，body 字段走 JSON body，两者分开传
- update_* tool：id 在 path，body 只传调用方提供的非 None 字段（_pick 函数），不发平台已有值
- delete_* tool：id 在 path，无 body
- 写操作的单测：mock rest_client.request，断言 method=PUT/POST/DELETE 及 body 内容；不做真实 SCM 调用（写操作有副作用，真实测试需 @integration 标注）
- description 里每个写操作 tool 都要标注「⚠️ 写操作」
```

**教学点**：SCM 写 API 的 container 参数（folder 等）走 query params 而不是 body——这是从 openapi YAML 现查得到的，不能臆造。`_pick()` 工具函数只取非 None 字段组装 body，让调用方可以只传要改的字段（PATCH 语义），而不强制要求传全量。

**验收**：写操作 tool 单测（mock）全部通过；`create_address` + `delete_address` 集成测试（`@integration`，默认跳过）可手动运行。

**提交**：
```bash
git add -A && git commit -m "step-4b: 实现 Objects API 写操作 tool（create/update/delete，_pick 函数）"
git tag step-4b && git push origin scm && git push origin step-4b
```

---

### Step 5 — 实现 Security / Operations / IAM tools

**真实提示词（逐字）**：

```
继续实现剩余三个 API 域的 tool，按 DESIGN §3.2–3.4 映射表，严格阶段 1→2 顺序。

Security（security-services-R2-2026.yaml）：
- security_rules：完整 CRUD（list/create/get/update/delete）
- 安全配置文件：list_anti_spyware_profiles、list_vulnerability_profiles、list_wildfire_profiles、list_dns_security_profiles、list_url_categories、list_decryption_rules、list_decryption_profiles——均只读，路由表驱动

Operations（config-operations-march.yaml）：
- list_jobs、get_job、list_config_versions——只读
- push_candidate_config（POST /config-versions/candidate:push）——写操作，⚠️ 会触发真实配置下发，description 必须清晰警示

IAM（ServiceAccounts/Roles/AccessPolicies YAML）：
- list_service_accounts、list_roles、list_access_policies——均只读

约束：
- push_candidate_config 的 body 有 folders/devices/admin/description 四个字段，从 YAML 现查，不臆造；folders 和 devices 互斥但可任选其一，不强制必填（交平台 400 处理）
- 安全配置文件类 tool（7 个只读）用同一路由表 _LIST_TOOLS 统一处理，不单独写 if/elif
- 每步 commit + pytest 单测（mock）
```

**教学点**：`push_candidate_config` 是本项目风险最高的 tool——它会真实下发配置到防火墙。description 里的 ⚠️ 警示不是装饰，是让 Claude 在调用前向用户确认的信号。7 个安全配置文件只读 tool 全部进 `_LIST_TOOLS`，证明路由表扩展零成本（加一行字典条目即可）。

**验收**：37 个 tool 全部注册；路由完整性验证通过（`set(TOOLS) == routed`）；`push_candidate_config` 单测验证 method=POST 且 body 字段正确。

**提交**：
```bash
git add -A && git commit -m "step-5: 实现 Security / Operations / IAM tools（37 个 tool 全部注册）"
git tag step-5 && git push origin scm && git push origin step-5
```

---

### Step 6 — 阶段 3 收口 + stdio 冒烟

**真实提示词（逐字）**：

```
执行 WORKFLOW.md 阶段 3：验收收口。先不扩新端点，把当前批次收口。先给计划我确认。

1. 语法自检：写一个内联脚本，对 src/scm_mcp/ 下全部 .py 文件跑 ast.parse，全通才算过。
2. 路由完整性验证：断言 TOOLS 列表中的 tool 名称集合 == 五张路由表的 key 合集，无遗漏、无多余。
3. stdio 冒烟（scripts/smoke_stdio.py）：用官方 mcp SDK 的 client over stdio 驱动本 server，跑完整握手：initialize → tools/list（断言 37 个 tool 且名称集合完全匹配）→ call_tool(list_jobs, {limit:1})，打印返回。证明它作为真实 MCP server 在传输层可用，而非只是直调 tools.call()。
4. 更新 README：补 37 个 tool 的分类列表；给出 Claude Desktop / Cursor 的注册 JSON（command/args/env=SCM_*/）；加"连通性自检"一节。
5. 更新 WORKFLOW.md 验收记录：对照 docs/PRD.md §4 的 A1–A7 逐条标注结论 + 验证命令/证据。

约束：不新增 tool；不改已有 tool 行为；docs/ 相关文件一并检查是否需要同步更新。
完成后给 commit message。
```

**教学点**：冒烟用真实 MCP **client** 驱动 server，证明**传输层**可用（而非只直调 `tools.call()`）。路由完整性验证是"不漏 tool"的机械保证。37 个 tool 如果靠人工数容易出错，程序断言不会。

**验收**：`python -c "import ast, ..."` → 7 文件全部 OK；路由完整性 → 37 tools, All routing entries present；`python scripts/smoke_stdio.py` → SMOKE OK；WORKFLOW 验收记录 A1–A7 全部填写。

**提交**：
```bash
git add -A && git commit -m "step-6: 阶段 3 收口（语法检查 + 路由完整性 + 冒烟 + README + WORKFLOW 验收记录）"
git tag step-6 && git push origin scm && git push origin step-6
```

---

## 3. SCM API 端点覆盖盘点

| 域 | 只读 tool | 写操作 tool | 排除/后续 |
| --- | --- | --- | --- |
| Objects | list/get × 地址/地址组 + list × 服务/服务组/标签/应用组/EDL | create/update/delete × 地址/地址组/服务/服务组/标签 + create_security_rule | SASE 网络配置等高复杂度端点（后续批次） |
| Security | list/get × 安全规则 + list × 7 类安全配置文件 | create/update/delete × 安全规则 | — |
| Operations | list_jobs / get_job / list_config_versions | push_candidate_config | — |
| IAM | list × 服务账号/角色/访问策略 | — | IAM 写操作（后续批次） |
| Auth | — | — | 全部内化到 auth.py，不暴露 tool |

合计：**37 tool（25 只读 + 12 写）**；Auth 域完全内化；高复杂度端点显式推迟。

---

## 4. 学生如何跟做

### 方式 A：对照已完成的仓库（最快）

```bash
git clone <repo>
cd vibecoding-mcp-server
git checkout scm

# 配置凭据
cp .env.example .env
# 编辑 .env 填入 SCM_CLIENT_ID / SCM_CLIENT_SECRET / SCM_TSG_ID

# 安装并自检
pip install -e .
export $(cat .env | grep -v '^#' | xargs)
python -m scm_mcp.check

# 冒烟测试
python scripts/smoke_stdio.py
```

### 方式 B：用上面的提示词从零复现

按 Step 0 → Step 6 顺序，把每节"真实提示词"原样发给 Claude Code（或 Cursor），对照教学点和验收标准确认每步结果。

关键习惯：
- **每步先给计划、等确认后再执行**（提示词里的 gating 不要删）。
- **阶段 1（填表）和阶段 2（写代码）严格不混**：先确认 DESIGN 映射表完整，再写任何 tool 代码。
- **写操作默认不做真实集成测试**：需要真实调用时加 `@pytest.mark.integration` 且默认 deselect。

---

## 5. 常见问题

| 问题 | 原因 | 解决 |
| --- | --- | --- |
| `RuntimeError: 环境变量 SCM_CLIENT_ID 未设置` | 未配置凭据 | 检查 `.env` 或环境变量是否正确导出 |
| `HTTP 401` | token 无效或 TSG_ID 不匹配 | 确认 CLIENT_SECRET 正确；确认 TSG_ID 是服务账号有权限的 TSG |
| `HTTP 403` | 服务账号权限不足 | 在 SCM → IAM 为服务账号分配更高权限角色 |
| `HTTP 400` on list | folder/snippet/device 参数缺失 | SCM 列表 API 要求至少提供一个容器参数 |
| tool 在 MCP 客户端不出现 | 会话未重启 | 关闭重开会话；确认 `scm-mcp` 已在 MCP 配置中注册 |
| `push_candidate_config` 返回 409 | 有其他 job 正在运行 | 先用 `list_jobs` 确认无 pending/running job 再推送 |
