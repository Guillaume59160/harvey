"""Local read-only preview of Harvey's actual dashboard, NOT a sales agent.

Run from checkout root after pip install -e .:
  python pilots/etatloc/dashboard_readonly.py
This program never runs Harvey's heartbeat. All HTTP mutations are rejected.
The UI may show actions, but buttons that write will return HTTP 403.
Do not expose this server with tunneling, proxies, Docker ports or public IPs.
"""
import os
from pathlib import Path

if __name__ == "__main__":
    import uvicorn
    from starlette.responses import PlainTextResponse
    from harvey import dashboard as dash

    root = Path(__file__).resolve().parents[2]
    data = root / "data"
    if (root / ".env").exists():
        raise SystemExit("BLOCK: .env exists in this checkout. Use a clean isolated clone.")
    if (data / "harvey.db").exists():
        raise SystemExit("BLOCK: existing Harvey database; use clean demo checkout.")
    cfg = root / "harvey.local.yaml"
    if cfg.exists():
        raise SystemExit("BLOCK: local override exists; clean demo checkout required.")
    from pilots.etatloc.preflight import check
    errors = check(root / "pilots" / "etatloc" / "harvey.yaml")
    if errors:
        raise SystemExit("BLOCK: " + "; ".join(errors))
    dash.CONFIG_FILE = root / "pilots" / "etatloc" / "harvey.yaml"

    @dash.app.middleware("http")
    async def block_mutations(request, call_next):
        if request.method not in ("GET", "HEAD"):
            return PlainTextResponse("Demo is read-only; action blocked", status_code=403)
        # Allow only the shell and a bounded set of harmless local display APIs.
        path = request.url.path
        allowed = {"/", "/api/setup-status", "/api/companies", "/api/prospects",
                   "/api/campaigns", "/api/conversations", "/api/activity",
                   "/api/stats", "/api/outbox", "/api/today", "/api/runs",
                   "/api/harvey/status", "/api/signals"}
        if path not in allowed and not path.startswith("/static/"):
            return PlainTextResponse("Demo endpoint disabled", status_code=403)
        return await call_next(request)

    print("Read-only Etatloc demo. Localhost only, no Harvey agent started.")
    print("Open this private unlock link: " + dash.dashboard_url(host="127.0.0.1", port=5555))
    print("Never share the link or expose the local server to the public network.")
    uvicorn.run(dash.app, host="127.0.0.1", port=5555,
                proxy_headers=False, server_header=False, date_header=False)
