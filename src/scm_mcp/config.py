"""配置读取：SCM API 凭据与端点均走环境变量，不硬编码。

SCM OAuth2 client_credentials 流程：
  - SCM_CLIENT_ID    : service account 的 client ID
  - SCM_CLIENT_SECRET: service account 的 client secret
  - SCM_TSG_ID       : Tenant Service Group ID（scope 参数）
  - SCM_AUTH_URL     : OAuth2 token 端点（默认 PAN 官方）
  - SCM_BASE_URL     : SCM config API 基址（默认 PAN 官方）
"""

import os

SCM_AUTH_URL_DEFAULT = "https://auth.apps.paloaltonetworks.com"
SCM_BASE_URL_DEFAULT = "https://api.strata.paloaltonetworks.com"


def get_auth_url() -> str:
    return os.environ.get("SCM_AUTH_URL", SCM_AUTH_URL_DEFAULT).rstrip("/")


def get_base_url() -> str:
    return os.environ.get("SCM_BASE_URL", SCM_BASE_URL_DEFAULT).rstrip("/")


def get_client_id() -> str:
    v = os.environ.get("SCM_CLIENT_ID", "")
    if not v:
        raise RuntimeError("环境变量 SCM_CLIENT_ID 未设置")
    return v


def get_client_secret() -> str:
    v = os.environ.get("SCM_CLIENT_SECRET", "")
    if not v:
        raise RuntimeError("环境变量 SCM_CLIENT_SECRET 未设置")
    return v


def get_tsg_id() -> str:
    v = os.environ.get("SCM_TSG_ID", "")
    if not v:
        raise RuntimeError("环境变量 SCM_TSG_ID 未设置")
    return v
