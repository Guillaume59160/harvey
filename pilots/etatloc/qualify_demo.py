"""Offline fictional-company qualification for Etatloc (no Harvey agent/LLM/network).

Run: python pilots/etatloc/qualify_demo.py
All inputs must be explicitly labelled demo/fictif; rejects anything else.
"""
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent
NEAR_LILLE = {"Lille", "Roubaix", "Tourcoing", "Villeneuve-d'Ascq", "Marcq-en-Barœul", "Armentières"}
CORE = {"Agence immobilière", "Administrateur de biens"}

def evaluate(row):
    if row["source"] != "demo" or row["status"] != "fictif" or not row["website"].endswith(".example"):
        raise ValueError("Refusing non-fictional company in offline pilot")
    reasons = []
    score = 0
    if row["management_activity"].strip().lower() == "oui":
        score += 60
        reasons.append("gestion locative déclarée dans la simulation")
    else:
        reasons.append("activité de gestion locative non déclarée")
    if row["city"] in NEAR_LILLE:
        score += 20
        reasons.append("zone métropole lilloise")
    if row["segment"] in CORE:
        score += 20
        reasons.append("acteur immobilier cible")
    elif row["segment"] == "Conciergerie":
        score += 10
        reasons.append("conciergerie à qualifier")
    return {"company_id": row["company_id"], "company_name": row["company_name"],
            "city": row["city"], "score": score,
            "priority": "haute" if score >= 80 else "moyenne" if score >= 60 else "faible",
            "reason": "; ".join(reasons), "synthetic": "oui"}

def run(source=BASE / "companies_demo.csv", target=BASE / "qualification_demo.csv"):
    with source.open(encoding="utf-8", newline="") as fh:
        records = list(csv.DictReader(fh))
    results = sorted((evaluate(row) for row in records), key=lambda x: (-x["score"], x["company_id"]))
    with target.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(results[0]) if results else [
            "company_id", "company_name", "city", "score", "priority", "reason", "synthetic"])
        writer.writeheader()
        writer.writerows(results)
    print(f"OFFLINE DEMO: {len(results)} fictional companies qualified; no email, no API calls")
    return results

if __name__ == "__main__":
    run()
