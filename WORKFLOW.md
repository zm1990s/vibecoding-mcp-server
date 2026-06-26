# WORKFLOW.md — L3 阶段协议

> 服从 `CLAUDE.md`（L1）与 `DESIGN.md`（L2）。本文件定义「做事的阶段与顺序」。

## 阶段 1：契约同步（Contract Sync）

**目标**：让 `DESIGN.md` 的映射表与 `openapi-specs/scm/` YAML 文件严格一致。

1. 阅读 `../pan.dev/openapi-specs/scm/` 下对应分类的 YAML 文件。
2. 遍历 `paths` 下每个 `(path, method)`，按 `DESIGN.md §2` 命名原则生成 tool 名。
3. 填充 `DESIGN.md §3` 映射表：每行只记录 tool 名、方法+路径、类型（只读/写）。
4. 排除 Out of Scope 端点（Auth token 获取、前端/登录相关、§5 列明的范围外项）。
5. **漂移处理**：若与现有 DESIGN 不一致，更新 DESIGN，**不要**改代码去迁就旧设计。

✅ 出口条件：DESIGN.md 映射表无 `_TBD_`，每行可在对应 YAML 中定位。

---

## 阶段 2：实现（Implement）

**目标**：按 DESIGN 注册全部 tools，实现"刷 token → 组装请求 → 调 REST → 透传响应"。

1. 读取环境变量：`SCM_CLIENT_ID` / `SCM_CLIENT_SECRET` / `SCM_TSG_ID` / `SCM_BASE_URL` / `SCM_AUTH_URL`。
2. 用官方 `mcp` SDK + stdio 传输启动 server（`server.py`）。
3. `auth.py`：实现 OAuth2 client_credentials 流程，token 有效期 15 分钟，提前 60 秒刷新。
4. `rest_client.py`：封装 httpx，统一注入 Authorization header，统一超时与错误结构。
5. `tools.py`：为映射表每一行注册一个 tool，inputSchema 取自 YAML，逻辑只有三步。
6. `check.py`：连通性自检，验证 token 可获取、基址可访问。

✅ 出口条件：`tools/list` 能列出映射表中全部 tool；每个 tool 可成功转调对应端点。

---

## 阶段 3：验收（Acceptance）

逐条对照下表，全绿才算完成。

| # | 检查项 | 通过标准 |
|---|---|---|
| C1 | 红线自检 | 全仓除默认值/README 外无硬编码地址；无业务鉴权逻辑（token 刷新除外）；只 stdio |
| C2 | 契约一致 | DESIGN 每个 tool 都能在 openapi-specs 找到对应端点，无臆造字段 |
| C3 | 语法通过 | `python -c "import ast; ..."` → 全部源文件无语法错误 |
| C4 | 路由完整 | `python -c "from scm_mcp import tools; print(len(tools.TOOL_REGISTRY))"` 输出 37 |
| C5 | stdio 冒烟 | `python scripts/smoke_stdio.py` → tools/list 列出全部 37 个 tool |
| C6 | 可换环境 | 改 `SCM_BASE_URL` 后请求目标随之改变，无需改代码 |

### 集成验收（需真实 SCM 凭据）

| # | 检查项 | 通过标准 |
|---|---|---|
| I1 | 连通自检 | `python -m scm_mcp.check` 输出 `OK: SCM API 连通` |
| I2 | 只读 tool | 调 `list_jobs` 返回 SCM 真实响应，字段与 YAML response schema 一致 |
| I3 | 写操作 tool | 调 `create_address` 后对象在 SCM 控制台可见 |
| I4 | token 刷新 | 持续调用超过 15 分钟无 401 错误 |

---

## 变更流程（SCM API 变更时）

```
SCM API 变了（新版 openapi-specs YAML）
  → 阶段 1：重新阅读 YAML，同步 DESIGN（先改设计）
  → 阶段 2：按新 DESIGN 改代码
  → 阶段 3：重新验收
```

**顺序不可颠倒**：永远先同步契约和设计，再动代码。
