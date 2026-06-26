# DESIGN.md — L2 设计

> 服从 `CLAUDE.md`（L1）。本文件定义「暴露哪些 MCP tool、各自包哪个 REST 端点、入参/出参来源」。

## 1. 数据来源声明（唯一权威）

本文件所有 tool 的 **input/output schema** 来源是 `../pan.dev/openapi-specs/scm/` 下的 YAML 文件。

- 不手抄、不臆造字段名/类型/必填性。
- 当 OpenAPI YAML 与本文件冲突时，**YAML 为准**，按 `WORKFLOW.md` 流程回写更新本文件。

## 2. 命名与映射原则

- **一个 REST 端点 → 一个 MCP tool**，不合并、不拆分（特殊情况在表中注明）。
- tool 命名 = 动作 + 资源，小写下划线：`list_addresses`、`create_security_rule`、`push_candidate_config`。
- tool 的 inputSchema 直接取自该端点的 path / query / body 参数（来自 YAML）。
- tool 的输出 = REST 响应原样透传，不二次加工。
- ⚠️ 写操作端点在 description 中标注「⚠️ 写操作」。

## 3. Tool ↔ 端点映射表

### 3.1 Objects API

**基址**：`/config/objects/v1`
**OpenAPI 规范**：`config/sase/objects/objects-june.yaml`

| MCP tool | HTTP + 路径 | 类型 |
|---|---|---|
| `list_addresses` | GET /addresses | 只读 |
| `create_address` | POST /addresses | ⚠️ 写 |
| `get_address` | GET /addresses/{id} | 只读 |
| `update_address` | PUT /addresses/{id} | ⚠️ 写 |
| `delete_address` | DELETE /addresses/{id} | ⚠️ 写 |
| `list_address_groups` | GET /address-groups | 只读 |
| `create_address_group` | POST /address-groups | ⚠️ 写 |
| `get_address_group` | GET /address-groups/{id} | 只读 |
| `update_address_group` | PUT /address-groups/{id} | ⚠️ 写 |
| `delete_address_group` | DELETE /address-groups/{id} | ⚠️ 写 |
| `list_services` | GET /services | 只读 |
| `create_service` | POST /services | ⚠️ 写 |
| `list_service_groups` | GET /service-groups | 只读 |
| `create_service_group` | POST /service-groups | ⚠️ 写 |
| `list_tags` | GET /tags | 只读 |
| `create_tag` | POST /tags | ⚠️ 写 |
| `list_application_groups` | GET /application-groups | 只读 |
| `list_external_dynamic_lists` | GET /external-dynamic-lists | 只读 |

### 3.2 Security API

**基址**：`/config/security/v1`
**OpenAPI 规范**：`config/sase/security/security-services-R2-2026.yaml`

| MCP tool | HTTP + 路径 | 类型 |
|---|---|---|
| `list_security_rules` | GET /security-rules | 只读 |
| `create_security_rule` | POST /security-rules | ⚠️ 写 |
| `get_security_rule` | GET /security-rules/{id} | 只读 |
| `update_security_rule` | PUT /security-rules/{id} | ⚠️ 写 |
| `delete_security_rule` | DELETE /security-rules/{id} | ⚠️ 写 |
| `list_anti_spyware_profiles` | GET /anti-spyware-profiles | 只读 |
| `list_vulnerability_profiles` | GET /vulnerability-protection-profiles | 只读 |
| `list_wildfire_profiles` | GET /wildfire-anti-virus-profiles | 只读 |
| `list_dns_security_profiles` | GET /dns-security-profiles | 只读 |
| `list_url_categories` | GET /url-categories | 只读 |
| `list_decryption_rules` | GET /decryption-rules | 只读 |
| `list_decryption_profiles` | GET /decryption-profiles | 只读 |

### 3.3 Operations API

**基址**：`/config/operations/v1`
**OpenAPI 规范**：`config/sase/operations/config-operations-march.yaml`

| MCP tool | HTTP + 路径 | 类型 |
|---|---|---|
| `list_jobs` | GET /jobs | 只读 |
| `get_job` | GET /jobs/{id} | 只读 |
| `list_config_versions` | GET /config-versions | 只读 |
| `push_candidate_config` | POST /config-versions/candidate:push | ⚠️ 写 |

### 3.4 IAM API

**基址**：`/iam/v1`
**OpenAPI 规范**：`iam/ServiceAccounts.yaml` / `iam/Roles.yaml` / `iam/AccessPolicies.yaml`

| MCP tool | HTTP + 路径 | 类型 |
|---|---|---|
| `list_service_accounts` | GET /iam/v1/service_accounts | 只读 |
| `list_roles` | GET /iam/v1/roles | 只读 |
| `list_access_policies` | GET /iam/v1/access_policies | 只读 |

## 4. 通用约定

- **base URL**：`SCM_BASE_URL`（默认 `https://api.strata.paloaltonetworks.com`）。
- **鉴权**：OAuth2 client_credentials，token 由 `auth.py` 自动刷新，tool 层无需关心。
- **容器参数**：`folder` / `snippet` / `device` 三选一，走 query params，至少提供其一。
- **分页**：`offset` + `limit`（SCM 默认 limit=200），走 query params。
- **错误处理**：REST 返回非 2xx 时，tool 返回 `{"error": true, "status": <int>, "body": <payload>}`。

## 5. 不在范围内

- Auth API（token 获取由 `auth.py` 内部处理，不暴露为 tool）。
- SASE deployment / mobile agent / network services 等高复杂度写操作（后续批次）。
- NGFW / Cloud NGFW 专属端点（后续批次）。
- 租户级别 bulk 操作（非标 REST，后续评估）。
