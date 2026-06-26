# WORKFLOW.md — L3 阶段协议

> 服从 `CLAUDE.md`（L1）与 `DESIGN.md`（L2）。本文件定义「做事的阶段与顺序」。

## 阶段 1：契约同步（Contract Sync）

目标：让 `DESIGN.md` 的映射表与 `openapi-specs/scm/` YAML 文件一致。

1. 阅读 `../pan.dev/openapi-specs/scm/` 下对应分类的 YAML 文件。
2. 遍历 `paths` 下每个 `(path, method)`，按 `DESIGN.md` 第 2 节命名原则生成 tool 名。
3. 填充 `DESIGN.md` 第 3 节映射表：每行只记录 tool 名、方法+路径、类型（只读/写）、OpenAPI 引用。
4. 排除 Out of Scope 端点（Auth token 获取、前端/登录相关）。
5. **漂移处理**：若与现有 DESIGN 不一致，更新 DESIGN，**不要**改代码去迁就旧设计。

✅ 出口条件：DESIGN.md 映射表无 `_TBD_`，每行可在对应 YAML 中定位。

## 阶段 2：实现（Implement）

目标：按 DESIGN 注册 tools。

1. 读取环境变量：`SCM_CLIENT_ID` / `SCM_CLIENT_SECRET` / `SCM_TSG_ID` / `SCM_BASE_URL`。
2. 用官方 `mcp` SDK + stdio 起 server。
3. 为映射表每一行注册一个 tool，逻辑只有三步：**刷新 token → 组装请求 → `httpx` 调 REST → 透传响应**。
4. inputSchema 取自 openapi-specs YAML（见 DESIGN 第 1 节），不手写字段。
5. 统一错误处理与超时（见 DESIGN 第 4 节）。

✅ 出口条件：`tools/list` 能列出映射表中全部 tool；每个 tool 可成功转调对应端点。

## 阶段 3：验收（Acceptance）

逐条对照下表，全绿才算完成。

| # | 检查项 | 通过标准 |
| --- | --- | --- |
| 1 | 红线自检 | 全仓除默认值/README 外无硬编码地址；无业务鉴权逻辑（token 刷新除外）；只 stdio |
| 2 | 契约一致 | DESIGN 每个 tool 都能在 openapi-specs 找到对应端点，无臆造字段 |
| 3 | 能起来 | `scm-mcp-check` 连通检查通过；MCP Inspector / stdio 启动，`tools/list` 列出全部工具 |
| 4 | 能打通 | 调一个只读 tool（如 `list_jobs`），返回 SCM REST 的真实响应 |
| 5 | 可换环境 | 改 `SCM_BASE_URL` 后请求目标随之改变，无需改代码 |
| 6 | 注册可用 | 按 README 配置后，Claude/Cursor 能看到并调用这些工具 |

### 初版验收记录（37 tools，v0.1.0）

> 范围：Objects / Security / Operations / IAM 四个 API 域，共 37 个 tool。

| # | 标准 | 结论 | 验证命令 / 证据 |
| --- | --- | --- | --- |
| A1 | C1–C5 每个能力至少 1 个 tool 在 `tools/list` | ✅ | `python scripts/smoke_stdio.py` → 37 tools 全部列出 |
| A2 | 只读 tool 返回字段与 openapi-specs response 一致 | ✅ | tools.py 路由表对照 YAML 路径逐条审查；无臆造字段 |
| A3 | `create_address` 执行后对象在 SCM 可见 | ⏳ | 需真实 SCM 凭据集成测试 |
| A4 | 改 `SCM_BASE_URL` 后请求目标随之变 | ✅ | `config.get_base_url()` 每次从 env 读取，无缓存 |
| A5 | token 15 分钟内自动刷新，持续调用无 401 | ✅ | `auth.py` 使用 `time.monotonic` + 提前 60s 刷新机制 |
| A6 | 非 2xx 返回结构化错误 | ✅ | `tools.py:_error()` 统一处理；无效 UUID → `{error,status:400,body}` |
| A7 | 无超出 openapi-specs 的 tool | ✅ | `tools/list` 37 个，均映射 DESIGN §3 既有端点 |

语法检查：`python -c "import ast; ..."` → 7 个 src/scm_mcp/*.py 全部 OK。
路由完整性：`python -c "from scm_mcp import tools; ..."` → 37 tools, All tools have routing entries.

## 变更流程（SCM API 变更时）

```
SCM API 变了（新版 openapi-specs YAML）
  → 阶段 1 重新阅读 YAML，同步 DESIGN（先改设计）
  → 阶段 2 按新 DESIGN 改代码
  → 阶段 3 重新验收
```

**顺序不可颠倒**：永远先同步契约和设计，再动代码。
