"""配置读取：SCM API 凭据与端点均走环境变量，不硬编码。

环境变量一览：
  SCM_CLIENT_ID     (必填) service account client ID
  SCM_CLIENT_SECRET (必填) service account client secret
  SCM_TSG_ID        (必填) Tenant Service Group ID（OAuth2 scope 参数）
  SCM_BASE_URL      (可选) SCM config API 基址，默认 PAN 官方
  SCM_AUTH_URL      (可选) OAuth2 token 端点，默认 PAN 官方
"""

import os

_BASE_URL_DEFAULT = "https://api.strata.paloaltonetworks.com"
_AUTH_URL_DEFAULT = "https://auth.apps.paloaltonetworks.com"


def get_base_url() -> str:
    return os.environ.get("SCM_BASE_URL", _BASE_URL_DEFAULT).rstrip("/")


def get_auth_url() -> str:
    return os.environ.get("SCM_AUTH_URL", _AUTH_URL_DEFAULT).rstrip("/")


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
