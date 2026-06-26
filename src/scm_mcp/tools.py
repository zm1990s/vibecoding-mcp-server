"""SCM MCP tool 定义与分发。

端点映射（源自 openapi-specs/scm）：

Objects API  (https://api.strata.paloaltonetworks.com/config/objects/v1)
  list_addresses          GET  /config/objects/v1/addresses
  create_address          POST /config/objects/v1/addresses
  get_address             GET  /config/objects/v1/addresses/{id}
  update_address          PUT  /config/objects/v1/addresses/{id}
  delete_address          DEL  /config/objects/v1/addresses/{id}
  list_address_groups     GET  /config/objects/v1/address-groups
  create_address_group    POST /config/objects/v1/address-groups
  get_address_group       GET  /config/objects/v1/address-groups/{id}
  update_address_group    PUT  /config/objects/v1/address-groups/{id}
  delete_address_group    DEL  /config/objects/v1/address-groups/{id}
  list_services           GET  /config/objects/v1/services
  create_service          POST /config/objects/v1/services
  list_service_groups     GET  /config/objects/v1/service-groups
  create_service_group    POST /config/objects/v1/service-groups
  list_tags               GET  /config/objects/v1/tags
  create_tag              POST /config/objects/v1/tags
  list_application_groups GET  /config/objects/v1/application-groups
  list_external_dynamic_lists GET /config/objects/v1/external-dynamic-lists

Security API (https://api.strata.paloaltonetworks.com/config/security/v1)
  list_security_rules     GET  /config/security/v1/security-rules
  create_security_rule    POST /config/security/v1/security-rules
  get_security_rule       GET  /config/security/v1/security-rules/{id}
  update_security_rule    PUT  /config/security/v1/security-rules/{id}
  delete_security_rule    DEL  /config/security/v1/security-rules/{id}
  list_anti_spyware_profiles  GET  /config/security/v1/anti-spyware-profiles
  list_vulnerability_profiles GET /config/security/v1/vulnerability-protection-profiles
  list_url_categories     GET  /config/security/v1/url-categories
  list_decryption_rules   GET  /config/security/v1/decryption-rules

Operations API (https://api.strata.paloaltonetworks.com/config/operations/v1)
  list_jobs               GET  /config/operations/v1/jobs
  get_job                 GET  /config/operations/v1/jobs/{id}
  push_candidate_config   POST /config/operations/v1/config-versions/candidate:push
  list_config_versions    GET  /config/operations/v1/config-versions

IAM API (https://api.strata.paloaltonetworks.com/iam/v1)
  list_service_accounts   GET  /iam/v1/service-accounts
  list_roles              GET  /iam/v1/roles
  list_access_policies    GET  /iam/v1/access-policies
"""

import mcp.types as types

from . import rest_client

# ─── 公共 inputSchema 片段 ────────────────────────────────────────────────────

_FOLDER_PARAM = {
    "folder": {
        "type": "string",
        "description": "目标 folder（如 'Prisma Access'、'Service Connections'、'Remote Networks'）",
    }
}
_SNIPPET_PARAM = {
    "snippet": {"type": "string", "description": "目标 snippet（与 folder/device 三选一）"}
}
_DEVICE_PARAM = {
    "device": {"type": "string", "description": "目标 device（与 folder/snippet 三选一）"}
}
_OFFSET_PARAM = {"offset": {"type": "integer", "description": "分页偏移，默认 0"}}
_LIMIT_PARAM = {"limit": {"type": "integer", "description": "每页条数，最大 200"}}
_NAME_PARAM = {"name": {"type": "string", "description": "按名称精确过滤（可选）"}}
_ID_PARAM = {"id": {"type": "string", "description": "对象 UUID（必填）"}}

_LIST_PARAMS = {**_NAME_PARAM, **_FOLDER_PARAM, **_SNIPPET_PARAM, **_DEVICE_PARAM, **_OFFSET_PARAM, **_LIMIT_PARAM}
_CONTAINER_PARAMS = {**_FOLDER_PARAM, **_SNIPPET_PARAM, **_DEVICE_PARAM}

# ─── Tool 定义 ────────────────────────────────────────────────────────────────

TOOLS: list[types.Tool] = [

    # ── Objects: Addresses ────────────────────────────────────────────────────
    types.Tool(
        name="list_addresses",
        description="列出地址对象（GET /config/objects/v1/addresses）。支持按 folder/snippet/device/name 过滤与分页。",
        inputSchema={
            "type": "object",
            "properties": _LIST_PARAMS,
            "required": [],
        },
    ),
    types.Tool(
        name="create_address",
        description="创建地址对象（POST /config/objects/v1/addresses）。支持 ip-netmask / ip-range / ip-wildcard / fqdn 四种类型。",
        inputSchema={
            "type": "object",
            "properties": {
                **_CONTAINER_PARAMS,
                "name": {"type": "string", "description": "地址名称（必填）"},
                "description": {"type": "string"},
                "ip_netmask": {"type": "string", "description": "CIDR，如 192.168.1.0/24"},
                "ip_range": {"type": "string", "description": "IP 范围，如 192.168.1.1-192.168.1.10"},
                "ip_wildcard": {"type": "string", "description": "通配符地址"},
                "fqdn": {"type": "string", "description": "完全限定域名"},
                "tag": {"type": "array", "items": {"type": "string"}, "description": "标签列表"},
            },
            "required": ["name"],
        },
    ),
    types.Tool(
        name="get_address",
        description="按 UUID 获取地址对象详情（GET /config/objects/v1/addresses/{id}）。",
        inputSchema={"type": "object", "properties": _ID_PARAM, "required": ["id"]},
    ),
    types.Tool(
        name="update_address",
        description="更新地址对象（PUT /config/objects/v1/addresses/{id}）。",
        inputSchema={
            "type": "object",
            "properties": {
                **_ID_PARAM,
                "name": {"type": "string"},
                "description": {"type": "string"},
                "ip_netmask": {"type": "string"},
                "ip_range": {"type": "string"},
                "ip_wildcard": {"type": "string"},
                "fqdn": {"type": "string"},
                "tag": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["id"],
        },
    ),
    types.Tool(
        name="delete_address",
        description="删除地址对象（DELETE /config/objects/v1/addresses/{id}）。⚠️ 写操作，不可撤销。",
        inputSchema={"type": "object", "properties": _ID_PARAM, "required": ["id"]},
    ),

    # ── Objects: Address Groups ───────────────────────────────────────────────
    types.Tool(
        name="list_address_groups",
        description="列出地址组（GET /config/objects/v1/address-groups）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),
    types.Tool(
        name="create_address_group",
        description="创建地址组（POST /config/objects/v1/address-groups）。支持 static（成员列表）或 dynamic（过滤器）两种类型。",
        inputSchema={
            "type": "object",
            "properties": {
                **_CONTAINER_PARAMS,
                "name": {"type": "string", "description": "地址组名称（必填）"},
                "description": {"type": "string"},
                "static": {"type": "array", "items": {"type": "string"}, "description": "静态成员地址名列表"},
                "dynamic": {
                    "type": "object",
                    "properties": {"filter": {"type": "string"}},
                    "description": "动态过滤器表达式",
                },
                "tag": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["name"],
        },
    ),
    types.Tool(
        name="get_address_group",
        description="按 UUID 获取地址组详情（GET /config/objects/v1/address-groups/{id}）。",
        inputSchema={"type": "object", "properties": _ID_PARAM, "required": ["id"]},
    ),
    types.Tool(
        name="update_address_group",
        description="更新地址组（PUT /config/objects/v1/address-groups/{id}）。",
        inputSchema={
            "type": "object",
            "properties": {
                **_ID_PARAM,
                "name": {"type": "string"},
                "description": {"type": "string"},
                "static": {"type": "array", "items": {"type": "string"}},
                "dynamic": {"type": "object", "properties": {"filter": {"type": "string"}}},
                "tag": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["id"],
        },
    ),
    types.Tool(
        name="delete_address_group",
        description="删除地址组（DELETE /config/objects/v1/address-groups/{id}）。⚠️ 写操作。",
        inputSchema={"type": "object", "properties": _ID_PARAM, "required": ["id"]},
    ),

    # ── Objects: Services ─────────────────────────────────────────────────────
    types.Tool(
        name="list_services",
        description="列出服务对象（GET /config/objects/v1/services）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),
    types.Tool(
        name="create_service",
        description="创建服务对象（POST /config/objects/v1/services）。需指定 tcp 或 udp 端口。",
        inputSchema={
            "type": "object",
            "properties": {
                **_CONTAINER_PARAMS,
                "name": {"type": "string", "description": "服务名称（必填）"},
                "description": {"type": "string"},
                "protocol": {
                    "type": "object",
                    "description": "协议定义，含 tcp 或 udp 字段，各含 port 字符串（如 '80' 或 '8080-8090'）",
                    "properties": {
                        "tcp": {"type": "object", "properties": {"port": {"type": "string"}, "source_port": {"type": "string"}}},
                        "udp": {"type": "object", "properties": {"port": {"type": "string"}, "source_port": {"type": "string"}}},
                    },
                },
                "tag": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["name"],
        },
    ),

    # ── Objects: Service Groups ───────────────────────────────────────────────
    types.Tool(
        name="list_service_groups",
        description="列出服务组（GET /config/objects/v1/service-groups）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),
    types.Tool(
        name="create_service_group",
        description="创建服务组（POST /config/objects/v1/service-groups）。",
        inputSchema={
            "type": "object",
            "properties": {
                **_CONTAINER_PARAMS,
                "name": {"type": "string", "description": "服务组名称（必填）"},
                "members": {"type": "array", "items": {"type": "string"}, "description": "服务成员名称列表（必填）"},
                "tag": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["name", "members"],
        },
    ),

    # ── Objects: Tags ─────────────────────────────────────────────────────────
    types.Tool(
        name="list_tags",
        description="列出标签（GET /config/objects/v1/tags）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),
    types.Tool(
        name="create_tag",
        description="创建标签（POST /config/objects/v1/tags）。",
        inputSchema={
            "type": "object",
            "properties": {
                **_CONTAINER_PARAMS,
                "name": {"type": "string", "description": "标签名称（必填）"},
                "color": {"type": "string", "description": "标签颜色（可选，如 'Red'、'Blue'）"},
                "comments": {"type": "string"},
            },
            "required": ["name"],
        },
    ),

    # ── Objects: Application Groups ───────────────────────────────────────────
    types.Tool(
        name="list_application_groups",
        description="列出应用组（GET /config/objects/v1/application-groups）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),

    # ── Objects: External Dynamic Lists ──────────────────────────────────────
    types.Tool(
        name="list_external_dynamic_lists",
        description="列出外部动态列表（EDL）（GET /config/objects/v1/external-dynamic-lists）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),

    # ── Security: Security Rules ──────────────────────────────────────────────
    types.Tool(
        name="list_security_rules",
        description=(
            "列出安全策略规则（GET /config/security/v1/security-rules）。"
            "支持按 folder/snippet/device/name 过滤，以及 position 参数（pre/post）。"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                **_LIST_PARAMS,
                "position": {
                    "type": "string",
                    "enum": ["pre", "post"],
                    "description": "规则位置：pre（前置）或 post（后置）",
                },
            },
            "required": [],
        },
    ),
    types.Tool(
        name="create_security_rule",
        description="创建安全策略规则（POST /config/security/v1/security-rules）。⚠️ 写操作。",
        inputSchema={
            "type": "object",
            "properties": {
                **_CONTAINER_PARAMS,
                "position": {"type": "string", "enum": ["pre", "post"]},
                "name": {"type": "string", "description": "规则名称（必填）"},
                "description": {"type": "string"},
                "action": {
                    "type": "string",
                    "enum": ["allow", "deny", "drop", "reset-client", "reset-server", "reset-both"],
                    "description": "规则动作（必填）",
                },
                "from": {"type": "array", "items": {"type": "string"}, "description": "源区域列表"},
                "to": {"type": "array", "items": {"type": "string"}, "description": "目标区域列表"},
                "source": {"type": "array", "items": {"type": "string"}, "description": "源地址列表"},
                "destination": {"type": "array", "items": {"type": "string"}, "description": "目标地址列表"},
                "application": {"type": "array", "items": {"type": "string"}, "description": "应用列表"},
                "service": {"type": "array", "items": {"type": "string"}, "description": "服务列表"},
                "source_user": {"type": "array", "items": {"type": "string"}},
                "category": {"type": "array", "items": {"type": "string"}},
                "tag": {"type": "array", "items": {"type": "string"}},
                "disabled": {"type": "boolean"},
                "log_setting": {"type": "string"},
                "profile_setting": {
                    "type": "object",
                    "properties": {
                        "group": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "required": ["name", "action"],
        },
    ),
    types.Tool(
        name="get_security_rule",
        description="按 UUID 获取安全策略规则详情（GET /config/security/v1/security-rules/{id}）。",
        inputSchema={"type": "object", "properties": _ID_PARAM, "required": ["id"]},
    ),
    types.Tool(
        name="update_security_rule",
        description="更新安全策略规则（PUT /config/security/v1/security-rules/{id}）。⚠️ 写操作。",
        inputSchema={
            "type": "object",
            "properties": {
                **_ID_PARAM,
                "name": {"type": "string"},
                "description": {"type": "string"},
                "action": {"type": "string", "enum": ["allow", "deny", "drop", "reset-client", "reset-server", "reset-both"]},
                "from": {"type": "array", "items": {"type": "string"}},
                "to": {"type": "array", "items": {"type": "string"}},
                "source": {"type": "array", "items": {"type": "string"}},
                "destination": {"type": "array", "items": {"type": "string"}},
                "application": {"type": "array", "items": {"type": "string"}},
                "service": {"type": "array", "items": {"type": "string"}},
                "tag": {"type": "array", "items": {"type": "string"}},
                "disabled": {"type": "boolean"},
            },
            "required": ["id"],
        },
    ),
    types.Tool(
        name="delete_security_rule",
        description="删除安全策略规则（DELETE /config/security/v1/security-rules/{id}）。⚠️ 写操作，不可撤销。",
        inputSchema={"type": "object", "properties": _ID_PARAM, "required": ["id"]},
    ),

    # ── Security: Profiles ────────────────────────────────────────────────────
    types.Tool(
        name="list_anti_spyware_profiles",
        description="列出反间谍软件（Anti-Spyware）安全配置文件（GET /config/security/v1/anti-spyware-profiles）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),
    types.Tool(
        name="list_vulnerability_profiles",
        description="列出漏洞防护（Vulnerability Protection）安全配置文件（GET /config/security/v1/vulnerability-protection-profiles）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),
    types.Tool(
        name="list_wildfire_profiles",
        description="列出 WildFire 防病毒配置文件（GET /config/security/v1/wildfire-anti-virus-profiles）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),
    types.Tool(
        name="list_dns_security_profiles",
        description="列出 DNS 安全配置文件（GET /config/security/v1/dns-security-profiles）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),
    types.Tool(
        name="list_url_categories",
        description="列出自定义 URL 分类（GET /config/security/v1/url-categories）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),
    types.Tool(
        name="list_decryption_rules",
        description="列出解密规则（GET /config/security/v1/decryption-rules）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),
    types.Tool(
        name="list_decryption_profiles",
        description="列出解密配置文件（GET /config/security/v1/decryption-profiles）。",
        inputSchema={"type": "object", "properties": _LIST_PARAMS, "required": []},
    ),

    # ── Operations: Jobs ──────────────────────────────────────────────────────
    types.Tool(
        name="list_jobs",
        description="列出配置任务/Job（GET /config/operations/v1/jobs）。用于查看 push/commit 任务状态。",
        inputSchema={
            "type": "object",
            "properties": {
                **_OFFSET_PARAM,
                **_LIMIT_PARAM,
            },
            "required": [],
        },
    ),
    types.Tool(
        name="get_job",
        description="按 ID 获取配置 Job 详情（GET /config/operations/v1/jobs/{id}）。",
        inputSchema={"type": "object", "properties": _ID_PARAM, "required": ["id"]},
    ),

    # ── Operations: Config Versions ───────────────────────────────────────────
    types.Tool(
        name="list_config_versions",
        description="列出配置版本历史（GET /config/operations/v1/config-versions）。",
        inputSchema={
            "type": "object",
            "properties": {**_OFFSET_PARAM, **_LIMIT_PARAM},
            "required": [],
        },
    ),
    types.Tool(
        name="push_candidate_config",
        description=(
            "将候选配置推送到指定 folder 或设备（POST /config/operations/v1/config-versions/candidate:push）。"
            "⚠️ 写操作：将触发实际配置下发。folder 或 devices 至少填一个。"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "folders": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "目标 folder 列表（如 ['Prisma Access', 'Mobile Users']）",
                },
                "devices": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "目标设备序列号列表",
                },
                "admin": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "指定管理员/服务账号列表（可选）",
                },
                "description": {"type": "string", "description": "推送描述（可选）"},
            },
            "required": [],
        },
    ),

    # ── IAM ───────────────────────────────────────────────────────────────────
    types.Tool(
        name="list_service_accounts",
        description="列出 IAM 服务账号（GET /iam/v1/service-accounts）。",
        inputSchema={"type": "object", "properties": {**_OFFSET_PARAM, **_LIMIT_PARAM}, "required": []},
    ),
    types.Tool(
        name="list_roles",
        description="列出 IAM 角色（GET /iam/v1/roles）。",
        inputSchema={"type": "object", "properties": {**_OFFSET_PARAM, **_LIMIT_PARAM}, "required": []},
    ),
    types.Tool(
        name="list_access_policies",
        description="列出 IAM 访问策略（GET /iam/v1/access-policies）。",
        inputSchema={"type": "object", "properties": {**_OFFSET_PARAM, **_LIMIT_PARAM}, "required": []},
    ),
]

# ─── 辅助函数 ─────────────────────────────────────────────────────────────────

def _error(status: int, body) -> dict:
    return {"error": True, "status": status, "body": body}


def _pick(d: dict, *keys: str) -> dict:
    """从 d 中取出非 None 的指定 key，用于组装 query params 或 request body。"""
    return {k: d[k] for k in keys if d.get(k) is not None}


# ─── 路由表：tool_name -> (method, path_template, param_mode) ────────────────
# param_mode: "list"=分页列表query, "id_path"=UUID在路径, "body"=JSON body, "id_body"=两者

_OBJ_BASE = "/config/objects/v1"
_SEC_BASE = "/config/security/v1"
_OPS_BASE = "/config/operations/v1"
_IAM_BASE = "/iam/v1"

# 无参 GET（列表）工具：(path, list_param_keys)
_LIST_TOOLS: dict[str, tuple[str, tuple]] = {
    "list_addresses":            (f"{_OBJ_BASE}/addresses",                      ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_address_groups":       (f"{_OBJ_BASE}/address-groups",                  ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_services":             (f"{_OBJ_BASE}/services",                        ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_service_groups":       (f"{_OBJ_BASE}/service-groups",                  ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_tags":                 (f"{_OBJ_BASE}/tags",                            ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_application_groups":   (f"{_OBJ_BASE}/application-groups",              ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_external_dynamic_lists":(f"{_OBJ_BASE}/external-dynamic-lists",         ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_security_rules":       (f"{_SEC_BASE}/security-rules",                  ("name", "folder", "snippet", "device", "offset", "limit", "position")),
    "list_anti_spyware_profiles":(f"{_SEC_BASE}/anti-spyware-profiles",           ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_vulnerability_profiles":(f"{_SEC_BASE}/vulnerability-protection-profiles",("name", "folder", "snippet", "device", "offset", "limit")),
    "list_wildfire_profiles":    (f"{_SEC_BASE}/wildfire-anti-virus-profiles",    ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_dns_security_profiles":(f"{_SEC_BASE}/dns-security-profiles",           ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_url_categories":       (f"{_SEC_BASE}/url-categories",                  ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_decryption_rules":     (f"{_SEC_BASE}/decryption-rules",                ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_decryption_profiles":  (f"{_SEC_BASE}/decryption-profiles",             ("name", "folder", "snippet", "device", "offset", "limit")),
    "list_jobs":                 (f"{_OPS_BASE}/jobs",                            ("offset", "limit")),
    "list_config_versions":      (f"{_OPS_BASE}/config-versions",                 ("offset", "limit")),
    "list_service_accounts":     (f"{_IAM_BASE}/service-accounts",               ("offset", "limit")),
    "list_roles":                (f"{_IAM_BASE}/roles",                           ("offset", "limit")),
    "list_access_policies":      (f"{_IAM_BASE}/access-policies",                 ("offset", "limit")),
}

# 按 UUID GET（单条）工具：path_prefix（会拼 /{id}）
_GET_BY_ID_TOOLS: dict[str, str] = {
    "get_address":       f"{_OBJ_BASE}/addresses",
    "get_address_group": f"{_OBJ_BASE}/address-groups",
    "get_security_rule": f"{_SEC_BASE}/security-rules",
    "get_job":           f"{_OPS_BASE}/jobs",
}

# DELETE 工具：path_prefix
_DELETE_TOOLS: dict[str, str] = {
    "delete_address":       f"{_OBJ_BASE}/addresses",
    "delete_address_group": f"{_OBJ_BASE}/address-groups",
    "delete_security_rule": f"{_SEC_BASE}/security-rules",
}

# POST 创建工具：(path, container_keys, body_keys)
_CREATE_TOOLS: dict[str, tuple[str, tuple, tuple]] = {
    "create_address": (
        f"{_OBJ_BASE}/addresses",
        ("folder", "snippet", "device"),
        ("name", "description", "ip_netmask", "ip_range", "ip_wildcard", "fqdn", "tag"),
    ),
    "create_address_group": (
        f"{_OBJ_BASE}/address-groups",
        ("folder", "snippet", "device"),
        ("name", "description", "static", "dynamic", "tag"),
    ),
    "create_service": (
        f"{_OBJ_BASE}/services",
        ("folder", "snippet", "device"),
        ("name", "description", "protocol", "tag"),
    ),
    "create_service_group": (
        f"{_OBJ_BASE}/service-groups",
        ("folder", "snippet", "device"),
        ("name", "members", "tag"),
    ),
    "create_tag": (
        f"{_OBJ_BASE}/tags",
        ("folder", "snippet", "device"),
        ("name", "color", "comments"),
    ),
    "create_security_rule": (
        f"{_SEC_BASE}/security-rules",
        ("folder", "snippet", "device"),
        ("name", "description", "action", "from", "to", "source", "destination",
         "application", "service", "source_user", "category", "tag", "disabled",
         "log_setting", "profile_setting"),
    ),
}

# PUT 更新工具：(path_prefix, body_keys)
_UPDATE_TOOLS: dict[str, tuple[str, tuple]] = {
    "update_address": (
        f"{_OBJ_BASE}/addresses",
        ("name", "description", "ip_netmask", "ip_range", "ip_wildcard", "fqdn", "tag"),
    ),
    "update_address_group": (
        f"{_OBJ_BASE}/address-groups",
        ("name", "description", "static", "dynamic", "tag"),
    ),
    "update_security_rule": (
        f"{_SEC_BASE}/security-rules",
        ("name", "description", "action", "from", "to", "source", "destination",
         "application", "service", "tag", "disabled"),
    ),
}


def call(name: str, arguments: dict):
    """分发 tool 调用，返回透传 payload 或结构化错误。同步函数，由 server 侧线程池调用。"""
    arguments = arguments or {}

    # ── 列表查询 ──
    if name in _LIST_TOOLS:
        path, param_keys = _LIST_TOOLS[name]
        params = _pick(arguments, *param_keys) or None
        status, body = rest_client.request("GET", path, params=params)
        return body if 200 <= status < 300 else _error(status, body)

    # ── 按 ID 单条查询 ──
    if name in _GET_BY_ID_TOOLS:
        path_prefix = _GET_BY_ID_TOOLS[name]
        obj_id = arguments["id"]
        status, body = rest_client.request("GET", f"{path_prefix}/{obj_id}")
        return body if 200 <= status < 300 else _error(status, body)

    # ── DELETE ──
    if name in _DELETE_TOOLS:
        path_prefix = _DELETE_TOOLS[name]
        obj_id = arguments["id"]
        status, body = rest_client.request("DELETE", f"{path_prefix}/{obj_id}")
        return body if 200 <= status < 300 else _error(status, body)

    # ── POST 创建 ──
    if name in _CREATE_TOOLS:
        path, container_keys, body_keys = _CREATE_TOOLS[name]
        params = _pick(arguments, *container_keys) or None
        payload = _pick(arguments, *body_keys)
        status, body = rest_client.request("POST", path, params=params, json=payload)
        return body if 200 <= status < 300 else _error(status, body)

    # ── PUT 更新 ──
    if name in _UPDATE_TOOLS:
        path_prefix, body_keys = _UPDATE_TOOLS[name]
        obj_id = arguments["id"]
        payload = _pick(arguments, *body_keys)
        status, body = rest_client.request("PUT", f"{path_prefix}/{obj_id}", json=payload)
        return body if 200 <= status < 300 else _error(status, body)

    # ── 特殊：push_candidate_config ──
    if name == "push_candidate_config":
        payload = _pick(arguments, "folders", "devices", "admin", "description")
        status, body = rest_client.request(
            "POST", f"{_OPS_BASE}/config-versions/candidate:push", json=payload
        )
        return body if 200 <= status < 300 else _error(status, body)

    raise ValueError(f"unknown tool: {name}")
