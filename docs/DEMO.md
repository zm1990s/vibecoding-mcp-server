# 现场演示脚本（5 分钟）

> 目标：现场展示「问一句自然语言 → Claude 自主调 SCM tool → 返回真实配置数据」。
> 本 server 是 stdio，由客户端按需拉起，**无需部署**。注册见 `README.md`。

## 演示前准备（务必）

1. **注册**（已做过则跳过）：
   ```bash
   claude mcp add scm \
     --env SCM_CLIENT_ID=<your-client-id> \
     --env SCM_CLIENT_SECRET=<your-client-secret> \
     --env SCM_TSG_ID=<your-tsg-id> \
     -- python -m scm_mcp.server
   ```
2. **新开一个会话**——MCP 在会话启动时加载，旧会话不会动态加载。
3. **连通性确认**：先运行 `python -m scm_mcp.check`，确保 token 获取和 API 连通正常。
4. **预热**：把 Demo 1、Demo 2 各跑一遍（避免冷启动延迟）。

---

## 0:00–0:30 · 立框架

> "这是一个 MCP server，把 Palo Alto Networks SCM 的 REST API 包了一层，让 Claude 直接操作防火墙策略配置。我没给它写任何业务逻辑，全靠 SCM 的 API。看。"

→ 打 `/mcp`，亮出 **scm，37 个 tool**。

---

## 0:30–1:30 · Demo 1（策略审计）

**问**：
> 列出 "Prisma Access" folder 下的安全策略规则，并告诉我有没有 action 为 allow 且 destination 为 any 的规则

预期：Claude 调 `list_security_rules`（folder="Prisma Access"），返回真实规则列表后自行分析，指出宽松规则。

> 话术："注意——是 Claude 自己决定调哪个工具、怎么传参数；我的 MCP server 只是把请求转给 SCM、把结果透传回来。"

---

## 1:30–2:30 · Demo 2（对象查询）

**问**：
> 帮我查一下现在有哪些地址组，列出名称和成员

预期：Claude 调 `list_address_groups`，返回地址组列表（含 static 成员或 dynamic 过滤器）。

**追问**（可选，展示 follow-up 能力）：
> 给我创建一个名叫 "test-demo-group"、包含成员 "10.0.0.1/32" 的静态地址组，放在 "Prisma Access" folder

预期：Claude 先调 `create_address`（创建地址对象），再调 `create_address_group`，返回创建结果的 UUID。

> ⚠️ 此步骤会真实写入 SCM，演示后记得用 `delete_address_group` / `delete_address` 清理。

---

## 2:30–3:30 · Demo 3（配置推送）

**问**：
> 有没有正在跑的配置 job？看一下最近的几个

预期：Claude 调 `list_jobs`，返回 jobs 列表（含 status: pending/running/success/failed）。

**可选追问**（如果有 pending job 的话）：
> 那个 ID 为 xxx 的 job 是什么状态，详情是什么

预期：Claude 调 `get_job`，返回 job 详情。

---

## 3:30–4:30 · Demo 4（安全配置文件审计）

**问**：
> 帮我看看现在有哪些 Anti-Spyware 配置文件，以及有没有漏洞防护（Vulnerability Protection）的配置文件

预期：Claude 并行（或顺序）调 `list_anti_spyware_profiles` 和 `list_vulnerability_profiles`，汇总返回。

---

## 4:30–5:00 · 收口

> "全程 37 个工具，覆盖 SCM 的对象管理、安全策略、配置推送、IAM 查询四大类。代码核心就三步：拿 token → 转发请求 → 透传响应。没有业务逻辑，完全由 Claude 自己决定用哪个工具、怎么组合。"

→ 打开 `src/scm_mcp/tools.py`，展示路由表的简洁性。

---

## 临场保险

| 问题 | 处理 |
| --- | --- |
| 调用返回 401 | token 刚过期，再调一次会自动刷新；若持续，检查 SCM_CLIENT_SECRET 是否正确 |
| 调用返回 403 | 服务账号权限不足，检查 SCM 中的角色分配 |
| list 结果为空 | folder 名称大小写敏感，确认 "Prisma Access" 拼写；或该 folder 确实无数据 |
| 工具不出现 | 重新开会话；或运行 `python -m scm_mcp.check` 确认连通性 |
