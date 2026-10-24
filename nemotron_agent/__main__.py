"""CLI for the Nemotron Integrity Agent.

  python -m nemotron_agent models                  check configured model ids and prices live
  python -m nemotron_agent triage --case ID|PATH   run one tamper-triage fixture end to end
  python -m nemotron_agent triage --live URL|PATH [--certified PATH] [--meta PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from . import config, triage
from .llm import NemotronClient, load_env

PKG = os.path.dirname(os.path.abspath(__file__))
CERTIFIED = os.path.join(PKG, "fixtures", "certified", "results.json")
CASES = os.path.join(PKG, "fixtures", "cases")


def load_case(ref: str) -> dict:
    path = ref if os.path.exists(ref) else os.path.join(CASES, ref.lower() + ".json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def case_live_bytes(case: dict, certified_bytes: bytes) -> bytes:
    from .seal import apply_patches
    live = apply_patches(json.loads(certified_bytes), case["patches"])
    return (json.dumps(live, indent=2, ensure_ascii=False) + "\n").encode()


def print_calls(calls) -> None:
    total = 0.0
    for c in calls:
        total += c.cost_usd
        status = "ok" if c.ok else f"FAILED ({c.error})"
        print(f"  {c.task:<16} {c.model:<40} in={c.prompt_tokens:>5} out={c.completion_tokens:>5} "
              f"(reasoning {c.reasoning_tokens:>4})  {c.latency_ms / 1000:5.1f}s  ${c.cost_usd:.5f}  {status}")
    print(f"  total estimated cost ${total:.5f}")


def cmd_models(_args) -> int:
    import urllib.request
    load_env()
    req = urllib.request.Request(config.BASE_URL + "models?verbose=true",
                                 headers={"Authorization": "Bearer " + os.environ["NEBIUS_API_KEY"]})
    with urllib.request.urlopen(req, timeout=30) as resp:
        live = {m["id"]: m for m in json.load(resp)["data"]}
    wanted = {**{r.role: r.model for r in config.routes().values()},
              "fast-candidate-2": config.NANO, "stretch-vl": config.SUPER_VL}
    ok = True
    for role, model in wanted.items():
        m = live.get(model)
        if not m:
            ok = False
            print(f"{role:<16} {model:<40} MISSING")
            continue
        price = m.get("pricing", {})
        p_in, p_out = float(price.get("prompt", 0)), float(price.get("completion", 0))
        drift = "" if (p_in, p_out) == config.PRICES.get(model) else "  (price differs from config!)"
        print(f"{role:<16} {model:<40} ${p_in * 1e6:.2f}/M in  ${p_out * 1e6:.2f}/M out  "
              f"ctx {m.get('context_length')}{drift}")
    return 0 if ok else 1


def cmd_triage(args) -> int:
    certified_bytes = open(args.certified, "rb").read()
    if args.case:
        case = load_case(args.case)
        live_bytes, meta = case_live_bytes(case, certified_bytes), case["metadata"]
        print(f"Case {case['id']}: {case['title']} (expected: {case['expected']})")
    else:
        from .seal import read_source
        live_bytes = read_source(args.live)
        meta = json.load(open(args.meta, encoding="utf-8")) if args.meta else {}
    out = triage.run(certified_bytes, live_bytes, meta, NemotronClient(), report=not args.no_report)
    seal = out["seal"]
    if args.json:
        print(json.dumps({**out, "calls": [c.__dict__ for c in out["calls"]]}, indent=2, ensure_ascii=False))
        return 0
    print(f"Seal: {'MATCH' if seal['match'] else 'MISMATCH'}  certified {seal['certified_sha256'][:12]}…  "
          f"live {seal['live_sha256'][:12]}…  ({len(seal['diff'])} changed fields)")
    for f in seal["findings"]:
        print(f"  [{f['severity']}] {f['rule_id']} {f['title']}")
    if out["triage"]:
        t = out["triage"]
        print(f"Nemotron verdict: {t['verdict'].upper()}  confidence {t['confidence']:.2f}  "
              f"-> {t['recommended_action']}\n  {t['summary']}")
        for e in t["evidence"]:
            print(f"  - ({e['points_to']}) {e['change']}: {e['observation']}")
    elif out["triage_error"]:
        print(f"Nemotron verdict: none ({out['triage_error']})")
    d = out["decision"]
    print(f"Gate decision: {d['action']}  ({d['reason']})")
    if out["incident_report_md"]:
        print("\n" + out["incident_report_md"] + "\n")
    print("Model calls:")
    print_calls(out["calls"])
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m nemotron_agent")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models", help="check model ids and prices on Token Factory")
    t = sub.add_parser("triage", help="tamper triage of certified vs live results")
    src = t.add_mutually_exclusive_group(required=True)
    src.add_argument("--case", help="fixture id (t01) or path")
    src.add_argument("--live", help="live results URL or path")
    t.add_argument("--certified", default=CERTIFIED)
    t.add_argument("--meta", help="change metadata JSON (with --live)")
    t.add_argument("--no-report", action="store_true", help="skip the incident report call")
    t.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    return {"models": cmd_models, "triage": cmd_triage}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
