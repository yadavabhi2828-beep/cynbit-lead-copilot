"""Offline evaluation of the deterministic baseline (no LLM).

Two sets:
  * data/sample_leads.json  - 17 synthetic leads written WHILE designing the rules (dev set; optimistic)
  * data/holdout_leads.json - 10 harder leads written BEFORE looking at rule behaviour (honest estimate, tiny n)
Both are synthetic. They are a regression harness and a demonstration of method, not a production claim.
Usage:  python eval/run_eval.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from copilot.pipeline import LeadCopilot  # noqa: E402
from copilot.schemas import Lead  # noqa: E402

SETS = {"dev": "sample_leads.json", "holdout": "holdout_leads.json"}


def evaluate(copilot: LeadCopilot, path: Path) -> tuple[dict, list]:
    data = json.loads(path.read_text(encoding="utf-8"))
    intent_ok = tier_ok = svc_ok = svc_n = hit_ok = hit_n = 0
    rows = []
    for item in data:
        exp, res = item["expected"], copilot.process(Lead(**item["lead"]))
        i_ok, t_ok = res.extraction.intent.value == exp["intent"], res.score.tier.value == exp["tier"]
        intent_ok += i_ok
        tier_ok += t_ok
        if exp["service_line"] not in (None, "unknown"):
            acceptable = exp["service_line"] if isinstance(exp["service_line"], list) else [exp["service_line"]]
            svc_n += 1
            svc_ok += res.extraction.service_line.value in acceptable
        if exp["relevant_docs"]:
            hit_n += 1
            hit_ok += any(e.id in exp["relevant_docs"] for e in res.evidence)
        rows.append((item["id"], exp["intent"], res.extraction.intent.value, exp["tier"], res.score.tier.value,
                     res.score.score, "OK" if i_ok and t_ok else "MISS"))
    n = len(data)
    return {"n_leads": n, "intent_accuracy": round(intent_ok / n, 3), "tier_accuracy": round(tier_ok / n, 3),
            "service_line_accuracy": round(svc_ok / max(svc_n, 1), 3),
            "retrieval_hit_rate": round(hit_ok / max(hit_n, 1), 3)}, rows


def main() -> dict:
    copilot = LeadCopilot(use_llm=False)
    out, lines = {}, ["# Evaluation results (offline deterministic baseline)", ""]
    for name, fname in SETS.items():
        metrics, rows = evaluate(copilot, ROOT / "data" / fname)
        out[name] = metrics
        lines += [f"## {name} set ({fname})", "", "| metric | value |", "|---|---|",
                  *[f"| {k} | {v} |" for k, v in metrics.items()], "",
                  "| id | expected intent | predicted intent | expected tier | predicted tier | score | status |",
                  "|---|---|---|---|---|---|---|", *[f"| {' | '.join(map(str, r))} |" for r in rows], ""]
    (ROOT / "eval" / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return out


if __name__ == "__main__":
    main()
