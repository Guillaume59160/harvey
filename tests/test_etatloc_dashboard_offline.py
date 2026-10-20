"""Harvey dashboard offline smoke: no credentials, no server, no agent process.

Uses FastAPI's in-process TestClient. No network or DB needed.
"""
from pathlib import Path

from fastapi.testclient import TestClient

import harvey.dashboard as dash


def test_etatloc_dashboard_shell_and_guards(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "DB_PATH", tmp_path / "does-not-exist.db")
    monkeypatch.setattr(dash, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setattr(dash, "CONFIG_FILE", Path(__file__).resolve().parents[1] / "pilots" / "etatloc" / "harvey.yaml")
    dash.token_store.configure(tmp_path / "dashboard-token")

    def cannot_spawn(*args, **kwargs):
        raise AssertionError("No agent process should be spawned in offline smoke")

    monkeypatch.setattr(dash.subprocess, "Popen", cannot_spawn)
    try:
        with TestClient(dash.app, base_url="http://127.0.0.1:5555") as client:
            page = client.get("/")
            assert page.status_code == 200
            assert "text/html" in page.headers["content-type"]
            assert page.headers["x-frame-options"] == "DENY"
            assert "no-store" in page.headers["cache-control"]
            assert client.get("/static/app.js").status_code == 200
            assert client.get("/api/companies").status_code == 401
            assert client.post("/api/settings/env", json={"SMTP_HOST": "bad.example"}).status_code == 401
            assert client.get("/", headers={"Host": "attacker.example"}).status_code == 400
        assert not (tmp_path / ".env").exists()
        assert not (tmp_path / "does-not-exist.db").exists()
    finally:
        dash.token_store.configure(dash.TOKEN_FILE)
