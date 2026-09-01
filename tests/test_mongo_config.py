"""Tests for optional Mongo settings."""

from __future__ import annotations

import mcp_bigquery.config as config_mod


def test_mongo_settings_defaults_and_allowlist(tmp_path, monkeypatch) -> None:
    cred = tmp_path / "sa.json"
    cred.write_text("{}")
    monkeypatch.setenv("JWT_ISSUER", "iss")
    monkeypatch.setenv("JWT_AUDIENCE", "aud")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(cred))
    monkeypatch.setenv("GCP_PROJECT_ID", "proj")
    monkeypatch.setenv("MONGO_ALLOWED_DATABASES", "prelisting, warehouse")
    monkeypatch.delenv("MONGO_URI", raising=False)
    config_mod._settings = None
    try:
        settings = config_mod.Settings()
        assert settings.mongo_uri is None
        assert settings.mongo_default_database == "prelisting"
        assert settings.allowed_mongo_databases == ("prelisting", "warehouse")
        assert settings.mongo_query_timeout_ms == 30_000
    finally:
        config_mod._settings = None
