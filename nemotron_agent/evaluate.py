"""Eval: accuracy, latency and cost per model on the fixture cases.

  python -m nemotron_agent eval [--repeats 2]

Two suites:
  triage   tamper triage (dev cases T01-T08 and held-out H01-H07), run on the REASONING role
           with each candidate model, thinking on. Scored on the verdict label.
  drift    translation-drift scenarios D1-D7, FAST extraction only (no explanation call),
           with each FAST candidate. Scored on the set of (language, field) mismatches.

Writes nemotron_agent/eval/results-<timestamp>.json (one file per run) and RESULTS.md (latest run).
"""

from __future__ import annotations

import datetime as dt
import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from . import config, multilingual, triage
from .__main__ import CASES, CERTIFIED, case_live_bytes, load_case
from .llm import NemotronClient

PKG = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(PKG, "eval")
HELDOUT = os.path.join(os.path.dirname(CASES), "heldout")
TRIAGE_MODELS = (config.SUPER, config.LIGHTNING, config.NANO)
FAST_MODELS = (config.LIGHTNING, config.NANO)
WORKERS = 4


def _cases(directory: str) -> list:
    return [load_case(os.path.join(directory, n)) for n in sorted(os.listdir(directory)) if n.endswith(".json")]


def _usage(calls) -> dict:
    return {"latency_ms": sum(c.latency_ms for c in calls), "cost_usd": sum(c.cost_usd for c in calls),
            "prompt_tokens": sum(c.prompt_tokens for c in calls),
            "completion_tokens": sum(c.completion_tokens for c in calls), "calls": len(calls)}


def run_triage_case(case: dict, model: str, split: str, repeat: int) -> dict:
    started = time.monotonic()
    cert = open(CERTIFIED, "rb").read()
    client = NemotronClient(routes={**config.routes(),
                                    "reasoning": config.Route("reasoning", model, 6000, True)})
    out = triage.run(cert, case_live_bytes(case, cert), case["metadata"], client, report=False)
    t = out["triage"]
    got = t["verdict"] if t else "error"
    return {"suite": "triage", "split": split, "case": case["id"], "model": model, "repeat": repeat,
            "expected": case["expected"], "got": got, "confidence": t["confidence"] if t else None,
            "decision": out["decision"]["action"], "correct": got == case["expected"],
            "error": out["triage_error"], "wall_ms": int((time.monotonic() - started) * 1000),
            **_usage(out["calls"])}


def run_drift_case(name: str, spec: dict, model: str, repeat: int) -> dict:
    started = time.monotonic()
    out = multilingual.run(multilingual.load_pages(name), NemotronClient(), fast_model=model, explain=False)
    got = sorted({(m["lang"], m["field"]) for m in out["mismatches"]})
    want = sorted({tuple(x) for x in spec["expected"]})
    tp = len(set(got) & set(want))
    return {"suite": "drift", "split": "eval", "case": spec["eval_id"], "model": model, "repeat": repeat,
            "expected": want, "got": got, "tp": tp, "fp": len(got) - tp, "fn": len(want) - tp,
            "correct": got == want, "kinds": sorted({m["kind"] for m in out["mismatches"]}),
            "error": "; ".join(out["errors"]) or None, "wall_ms": int((time.monotonic() - started) * 1000),
            **_usage(out["calls"])}


def summarize(rows: list) -> list:
    groups = {}
    for r in rows:
        groups.setdefault((r["suite"], r["split"], r["model"]), []).append(r)
    out = []
    for (suite, split, model), rs in sorted(groups.items()):
        row = {"suite": suite, "split": split, "model": model, "runs": len(rs),
               "cases": len({r["case"] for r in rs}),
               "correct": sum(r["correct"] for r in rs),
               "accuracy": sum(r["correct"] for r in rs) / len(rs),
               "median_latency_s": statistics.median(r["wall_ms"] for r in rs) / 1000,
               "mean_cost_usd": sum(r["cost_usd"] for r in rs) / len(rs),
               "errors": sum(1 for r in rs if r["error"])}
        if suite == "triage":
            not_tamper = [r for r in rs if r["expected"] != "tampering"]
            tamper = [r for r in rs if r["expected"] == "tampering"]
            row.update(false_rollback=sum(r["decision"] == "ROLLBACK" for r in not_tamper),
                       not_tamper_runs=len(not_tamper),
                       missed_tamper=sum(r["decision"] == "HUMAN_SIGNOFF" for r in tamper),
                       tamper_runs=len(tamper))
        if suite == "drift":
            tp, fp, fn = (sum(r[k] for r in rs) for k in ("tp", "fp", "fn"))
            row.update(tp=tp, fp=fp, fn=fn, precision=tp / (tp + fp) if tp + fp else 1.0,
                       recall=tp / (tp + fn) if tp + fn else 1.0)
        out.append(row)
    return out


def to_markdown(summary: list, rows: list, meta: dict) -> str:
    short = lambda m: m.split("/")[-1]  # noqa: E731
    lines = [f"# Eval results ({meta['date']})", "",
             f"Repeats per case and model: {meta['repeats']}. Temperature 0. Triage prompt SHA-256 "
             f"`{meta['triage_prompt_sha256'][:12]}…`. Small fixture sets: read these as a sanity check, "
             "not a benchmark. Latency is wall-clock per run with 4 runs in flight at once (drift runs its "
             "4 language extractions in parallel); a run that ends in an error still counts as wrong.", "",
             "## Summary", "",
             "| Suite | Split | Model | Cases | Runs | Correct | Accuracy | Median latency | Mean cost/run |",
             "|---|---|---|---|---|---|---|---|---|"]
    for s in summary:
        extra = f" (P {s['precision']:.2f} / R {s['recall']:.2f})" if s["suite"] == "drift" else ""
        lines.append(f"| {s['suite']} | {s['split']} | {short(s['model'])} | {s['cases']} | {s['runs']} | "
                     f"{s['correct']} | {s['accuracy']:.0%}{extra} | {s['median_latency_s']:.1f} s | "
                     f"${s['mean_cost_usd']:.5f} |")
    lines += ["", "## Gate outcomes (triage)", "",
              "What the gate did with each verdict. A false rollback replaces live results with the "
              "certified copy and alerts an official; a missed tampering leaves tampered numbers live "
              "until the official's sign-off review.", "",
              "| Split | Model | False rollbacks (legitimate or uncertain cases) | Tampering sent to sign-off as legitimate |",
              "|---|---|---|---|"]
    for s in summary:
        if s["suite"] == "triage":
            lines.append(f"| {s['split']} | {short(s['model'])} | {s['false_rollback']} of {s['not_tamper_runs']} | "
                         f"{s['missed_tamper']} of {s['tamper_runs']} |")
    lines += ["", "## Per case", "", "| Suite | Case | Model | Expected | Got (per repeat) |", "|---|---|---|---|---|"]
    per = {}
    for r in rows:
        per.setdefault((r["suite"], r["case"], r["model"]), []).append(r)
    fmt = lambda v: v if isinstance(v, str) else (", ".join(f"{a}:{b}" for a, b in v) or "none")  # noqa: E731
    for (suite, case, model), rs in sorted(per.items()):
        got = " / ".join(("✅ " if r["correct"] else "❌ ") + fmt(r["got"]) +
                         (f" {r['confidence']:.2f}" if r.get("confidence") is not None else "")
                         for r in sorted(rs, key=lambda r: r["repeat"]))
        lines.append(f"| {suite} | {case} | {short(model)} | {fmt(rs[0]['expected'])} | {got} |")
    return "\n".join(lines) + "\n"


def write(result: dict, stamp: str) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"results-{stamp}.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "RESULTS.md"), "w", encoding="utf-8") as fh:
        fh.write(to_markdown(result["summary"], result["rows"], result["meta"]))


def main(repeats: int = 1, suites=("triage", "drift")) -> dict:
    import hashlib
    jobs = []
    if "triage" in suites:
        for split, directory in (("dev", CASES), ("heldout", HELDOUT)):
            for case in _cases(directory):
                for model in TRIAGE_MODELS:
                    for rep in range(repeats):
                        jobs.append(lambda c=case, m=model, s=split, r=rep: run_triage_case(c, m, s, r))
    if "drift" in suites:
        with open(os.path.join(multilingual.I18N, "scenarios.json"), encoding="utf-8") as fh:
            scenarios = {k: v for k, v in json.load(fh).items() if not k.startswith("_") and "eval_id" in v}
        for name, spec in scenarios.items():
            for model in FAST_MODELS:
                for rep in range(repeats):
                    jobs.append(lambda n=name, sp=spec, m=model, r=rep: run_drift_case(n, sp, m, r))
    NemotronClient().transport  # fail fast on a missing key
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        rows = list(pool.map(lambda job: job(), jobs))
    meta = {"date": dt.date.today().isoformat(), "repeats": repeats, "workers": WORKERS,
            "triage_prompt_sha256": hashlib.sha256(triage.TRIAGE_SYSTEM.encode()).hexdigest(),
            "prices_source": config.PRICES_SOURCE}
    result = {"meta": meta, "summary": summarize(rows), "rows": rows}
    write(result, dt.datetime.now().strftime("%Y%m%d-%H%M"))
    return result
