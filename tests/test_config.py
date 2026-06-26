"""config 模块：环境变量读取与缺失时的错误行为。"""

import pytest

from scm_mcp import config


def test_base_url_default(monkeypatch):
    monkeypatch.delenv("SCM_BASE_URL", raising=False)
    assert config.get_base_url() == "https://api.strata.paloaltonetworks.com"


def test_base_url_override(monkeypatch):
    monkeypatch.setenv("SCM_BASE_URL", "https://my-scm.example.com/")
    assert config.get_base_url() == "https://my-scm.example.com"  # 去尾斜杠


def test_auth_url_default(monkeypatch):
    monkeypatch.delenv("SCM_AUTH_URL", raising=False)
    assert config.get_auth_url() == "https://auth.apps.paloaltonetworks.com"


def test_auth_url_override(monkeypatch):
    monkeypatch.setenv("SCM_AUTH_URL", "https://auth.example.com/")
    assert config.get_auth_url() == "https://auth.example.com"


def test_client_id_missing(monkeypatch):
    monkeypatch.delenv("SCM_CLIENT_ID", raising=False)
    with pytest.raises(RuntimeError, match="SCM_CLIENT_ID"):
        config.get_client_id()


def test_client_secret_missing(monkeypatch):
    monkeypatch.delenv("SCM_CLIENT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="SCM_CLIENT_SECRET"):
        config.get_client_secret()


def test_tsg_id_missing(monkeypatch):
    monkeypatch.delenv("SCM_TSG_ID", raising=False)
    with pytest.raises(RuntimeError, match="SCM_TSG_ID"):
        config.get_tsg_id()


def test_all_required_set(monkeypatch):
    monkeypatch.setenv("SCM_CLIENT_ID", "cid")
    monkeypatch.setenv("SCM_CLIENT_SECRET", "secret")
    monkeypatch.setenv("SCM_TSG_ID", "tsg123")
    assert config.get_client_id() == "cid"
    assert config.get_client_secret() == "secret"
    assert config.get_tsg_id() == "tsg123"
