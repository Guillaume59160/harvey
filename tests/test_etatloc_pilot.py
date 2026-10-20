"""Offline Etatloc pilot safety checks."""
from pathlib import Path
import importlib.util

import yaml

BASE = Path(__file__).resolve().parents[1] / "pilots" / "etatloc"
spec = importlib.util.spec_from_file_location("etatloc_preflight", BASE / "preflight.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_offline_pilot_disables_outreach():
    assert module.check(BASE / "harvey.yaml") == []


def test_sample_companies_are_explicitly_fictional():
    import csv
    with (BASE / "companies_demo.csv").open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 10
    assert all(r["status"] == "fictif" and r["source"] == "demo" for r in rows)
    assert all(r["website"].endswith(".example") for r in rows)


def test_preflight_rejects_enabled_email(tmp_path):
    data = yaml.safe_load((BASE / "harvey.yaml").read_text(encoding="utf-8"))
    data["channels"]["email"]["enabled"] = True
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    assert any("Email" in s for s in module.check(path))
