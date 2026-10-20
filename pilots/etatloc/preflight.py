"""Fail-closed preflight for the Etatloc demonstration profile.

No network, no credentials, no database writes. Python + PyYAML installed
with Harvey. Usage: python pilots/etatloc/preflight.py
"""
from pathlib import Path
import sys
import yaml

HERE = Path(__file__).resolve().parent

def check(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors = []
    email = data.get("channels", {}).get("email", {})
    linkedin = data.get("channels", {}).get("linkedin", {})
    if email.get("enabled") is not False:
        errors.append("Email must remain disabled")
    if email.get("max_daily_sends") != 0:
        errors.append("Daily email limit must be zero")
    if email.get("require_approval") is not True:
        errors.append("Human approval must be required")
    if linkedin.get("enabled") is not False:
        errors.append("LinkedIn must remain disabled")
    if linkedin.get("max_daily_connections") != 0 or linkedin.get("max_daily_messages") != 0:
        errors.append("LinkedIn limits must be zero")
    if data.get("persona", {}).get("company") != "Étatloc":
        errors.append("Expected Etatloc demo persona")
    return errors

if __name__ == "__main__":
    errors = check(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "harvey.yaml")
    for err in errors:
        print("BLOCK:", err)
    if errors:
        raise SystemExit(1)
    print("PASS: Etatloc pilot messaging disabled and approval required")
