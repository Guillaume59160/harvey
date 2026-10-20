"""Preflight check for the *resolved* hardened Docker Compose configuration.

Usage:
  export HARVEY_CLAUDE_AUTH_DIR=/absolute/dedicated/profile
  docker compose -f docker-compose.yml -f docker-compose.security.yml config --format json \
      | python scripts/check_security_compose.py
This script only validates config; it does not deploy anything.
"""
import json
import os
import sys
from pathlib import Path


def validate(config: dict, expected_auth: str) -> list[str]:
    errors = []
    service = config.get("services", {}).get("harvey", {})
    if not service:
        return ["Harvey service missing"]
    if service.get("privileged", False):
        errors.append("Container is privileged")
    if service.get("ports"):
        errors.append("Ports published; dashboard must stay private")
    if "ALL" not in service.get("cap_drop", []):
        errors.append("Missing cap_drop ALL")
    opts = service.get("security_opt", [])
    if "no-new-privileges:true" not in opts and "no-new-privileges" not in opts:
        errors.append("Missing no-new-privileges")
    vols = service.get("volumes", [])
    claude = []
    for vol in vols:
        if isinstance(vol, dict):
            source, dest = vol.get("source", ""), vol.get("target", "")
        else:
            parts = str(vol).split(":")
            source, dest = (parts[0], parts[1]) if len(parts) >= 2 else ("", "")
        if dest == "/home/harvey/.claude":
            claude.append(source)
        if source in ("/var/run/docker.sock", "/run/docker.sock"):
            errors.append("Docker socket mount prohibited")
    if len(claude) != 1 or claude[0] != expected_auth:
        errors.append("Claude mount must resolve to exactly the dedicated directory")
    if not Path(expected_auth).is_absolute():
        errors.append("Dedicated Claude directory must be absolute")
    return errors


def main() -> int:
    expected = os.environ.get("HARVEY_CLAUDE_AUTH_DIR", "")
    try:
        data = json.load(sys.stdin)
    except (ValueError, TypeError) as exc:
        print("Invalid Compose JSON:", exc, file=sys.stderr)
        return 2
    errors = validate(data, expected)
    if errors:
        for error in errors:
            print("BLOCK:", error, file=sys.stderr)
        return 1
    print("PASS: resolved Compose security invariants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
