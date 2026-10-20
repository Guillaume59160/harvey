"""The offline Etatloc sample must never mix real contacts into demo results."""
from pathlib import Path
import importlib.util
import csv
import pytest

BASE = Path(__file__).resolve().parents[1] / "pilots" / "etatloc"
spec = importlib.util.spec_from_file_location("etatloc_qualification", BASE / "qualify_demo.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_qualification_of_fictional_companies(tmp_path):
    results = mod.run(target=tmp_path / "results.csv")
    assert len(results) == 10
    assert all(x["synthetic"] == "oui" for x in results)
    assert all(0 <= x["score"] <= 100 for x in results)
    assert any(x["priority"] == "faible" for x in results)
    assert (tmp_path / "results.csv").exists()

def test_real_records_are_rejected():
    with pytest.raises(ValueError):
        mod.evaluate({"source":"web","status":"real","website":"https://real.com"})

def test_qualification_matches_reference_csv(tmp_path):
    generated = tmp_path / "qualification.csv"
    mod.run(target=generated)
    expected = BASE / "qualification_attendue.csv"
    with generated.open(encoding="utf-8", newline="") as fh:
        actual = list(csv.DictReader(fh))
    with expected.open(encoding="utf-8", newline="") as fh:
        reference = list(csv.DictReader(fh))
    assert actual == reference
