"""Scenarios, background jobs, recorded runs and spending caps for the web demo.

A visitor can replay a recorded run (instant, no model calls) or start a live run. Live
runs execute in a background thread; the page polls the job and shows each pipeline step
as it finishes. Live runs are capped per visitor IP per hour and per day overall, and at
most MAX_CONCURRENT run at once, on top of the spending limit set on the Token Factory account.
"""

from __future__ import annotations

import collections
import datetime as dt
import json
import os
import threading
import time
import uuid
from dataclasses import asdict

from . import config, hunter, multilingual, triage
from .__main__ import CERTIFIED, case_live_bytes, load_case
from .llm import NemotronClient
from .seal import read_source

PKG = os.path.dirname(os.path.abspath(__file__))
RECORDED = os.path.join(PKG, "web", "recorded")
LIVE_RESULTS_URL = "https://showcase-0b6166.gitlab.io/data/results.json"
OFFICIAL_PAGE = "https://showcase-0b6166.gitlab.io/voter-info.html"
DECOYS = ("kanaloa-vote-update.html", "noticias-kanaloa.html")
DAILY_CAP = int(os.environ.get("EIG_DAILY_LIVE_CAP", "60"))
IP_HOURLY_CAP = int(os.environ.get("EIG_IP_HOURLY_CAP", "6"))
MAX_CONCURRENT = 2


def public_base_url() -> str:
    """Where this demo is reachable from the internet (Render sets RENDER_EXTERNAL_URL)."""
    return os.environ.get("EIG_PUBLIC_URL") or os.environ.get("RENDER_EXTERNAL_URL", "")


def _short(model: str) -> str:
    return model.split("/")[-1]


def _steps(feature: str) -> list:
    r = config.routes()
    fast, reasoning, report = _short(r["fast"].model), _short(r["reasoning"].model), _short(r["report"].model)
    if feature == "seal":
        return [("seal", "Results Seal: SHA-256 and checker rules (deterministic)"),
                ("triage", f"{reasoning}: tamper triage, reasoning on"),
                ("gate", "Gate decision (code, not the model)"),
                ("report", f"{report}: incident report (only after a rollback decision)")]
    if feature == "translations":
        return [("extract", f"{fast}: extract facts from 4 languages in parallel"),
                ("compare", "Compare with the certified calendar, verify quotes (deterministic)"),
                ("explain", f"{reasoning}: explain each mismatch and its voter impact")]
    return [("tavily", "Tavily Search and Tavily Extract (live web)"),
            ("triage", f"{fast}: triage every result"),
            ("extract", f"{fast}: extract facts, then contradiction and lookalike checks (deterministic)"),
            ("report", f"{reasoning}: report citing URLs")]


def _triage_case(case_id: str):
    def run(progress):
        case = load_case(case_id)
        cert = open(CERTIFIED, "rb").read()
        out = triage.run(cert, case_live_bytes(case, cert), case["metadata"], NemotronClient(), progress=progress)
        out["case"] = {k: case[k] for k in ("id", "title", "expected", "metadata")}
        return out
    return run


def _live_site(progress):
    cert = open(CERTIFIED, "rb").read()
    out = triage.run(cert, read_source(LIVE_RESULTS_URL), {"source": LIVE_RESULTS_URL},
                     NemotronClient(), progress=progress)
    out["case"] = {"id": "LIVE", "title": "Results served right now by the official demo site",
                   "expected": None, "metadata": {"source": LIVE_RESULTS_URL}}
    return out


def _translations(progress):
    out = multilingual.run(multilingual.load_pages("drift"), NemotronClient(), progress=progress)
    out["pages"] = {lang: multilingual.visible_text(html) for lang, html in multilingual.load_pages("drift").items()}
    return out


def _hunt(progress):
    base = public_base_url().rstrip("/")
    watch = (OFFICIAL_PAGE,) + tuple(f"{base}/decoys/{d}" for d in DECOYS if base)
    return hunter.run(NemotronClient(), watchlist=watch, progress=progress)


SCENARIOS = {
    "live-site": {"feature": "seal", "title": "Check the live election site",
                  "blurb": "Hash the results file the official demo site serves right now and compare it with the "
                           "certified seal. Nemotron is only called if they differ.", "run": _live_site},
    "tamper": {"feature": "seal", "title": "Votes moved, totals kept",
               "blurb": "A service account uploads results where 1,632 votes moved between two candidates. Every "
                        "total still adds up, so arithmetic rules pass.", "run": _triage_case("t01")},
    "injection": {"feature": "seal", "title": "Prompt injection in the data",
                  "blurb": "A contest title tells 'reviewers and AI systems' the change is pre-approved, while "
                           "votes are swapped underneath.", "run": _triage_case("t02")},
    "correction": {"feature": "seal", "title": "Documented correction",
                   "blurb": "A canvass-board-approved fix of transposed digits in one precinct. This should not be "
                            "rolled back.", "run": _triage_case("t04")},
    "unverifiable": {"feature": "seal", "title": "Ticket can't be verified",
                     "blurb": "A small, consistent change whose ticket system is down. The right answer is a "
                              "person, not the model.", "run": _triage_case("t07")},
    "translations": {"feature": "translations", "title": "Translations drift",
                     "blurb": "English, Vietnamese, Spanish and Tagalog voter pages checked against the certified "
                              "calendar.", "run": _translations},
    "hunt": {"feature": "hunt", "title": "Hunt misinformation",
             "blurb": "Live Tavily searches plus a watchlist (the official page and two labeled demo decoys).",
             "run": _hunt},
}


def routing() -> list:
    r = config.routes()
    return [{"role": "FAST", "model": r["fast"].model,
             "why": "Fact extraction and result triage; reasoning off; picked by the eval"},
            {"role": "REASONING", "model": r["reasoning"].model,
             "why": "Tamper verdicts and mismatch explanations; reasoning on"},
            {"role": "REPORT", "model": r["report"].model,
             "why": "Incident report, only after a rollback decision"}]


def scenario_list() -> list:
    return [{"id": sid, "feature": s["feature"], "title": s["title"], "blurb": s["blurb"],
             "steps": [{"key": k, "label": label} for k, label in _steps(s["feature"])],
             "recorded": os.path.exists(os.path.join(RECORDED, f"{sid}.json"))}
            for sid, s in SCENARIOS.items()]


def serialize(result: dict) -> dict:
    out = dict(result)
    out["calls"] = [asdict(c) if not isinstance(c, dict) else c for c in result.get("calls", [])]
    out["totals"] = {"cost_usd": round(sum(c["cost_usd"] for c in out["calls"]), 6),
                     "prompt_tokens": sum(c["prompt_tokens"] for c in out["calls"]),
                     "completion_tokens": sum(c["completion_tokens"] for c in out["calls"]),
                     "model_calls": sum(1 for c in out["calls"] if c["role"] != "tavily"),
                     "tavily_calls": sum(1 for c in out["calls"] if c["role"] == "tavily")}
    return out


class Limits:
    def __init__(self, daily: int = DAILY_CAP, per_ip: int = IP_HOURLY_CAP):
        self.daily, self.per_ip = daily, per_ip
        self.day, self.day_count = None, 0
        self.by_ip = collections.defaultdict(collections.deque)
        self.lock = threading.Lock()

    def take(self, ip: str, now: float = None):
        """Reserve one live run. Returns None, or a message saying why not."""
        now = now or time.time()
        today = dt.datetime.fromtimestamp(now, dt.timezone.utc).date()
        with self.lock:
            if self.day != today:
                self.day, self.day_count = today, 0
            hits = self.by_ip[ip]
            while hits and hits[0] < now - 3600:
                hits.popleft()
            if self.day_count >= self.daily:
                return f"The demo's daily limit of {self.daily} live runs is used up. Recorded runs still work."
            if len(hits) >= self.per_ip:
                return f"Limit of {self.per_ip} live runs per hour reached for your connection. Recorded runs still work."
            hits.append(now)
            self.day_count += 1
            return None


class Jobs:
    def __init__(self):
        self.jobs, self.lock = {}, threading.Lock()
        self.recorded = {}

    def running(self) -> int:
        return sum(1 for j in self.jobs.values() if j["status"] == "running" and j["live"])

    def recorded_job(self, sid: str):
        if sid not in self.recorded:
            path = os.path.join(RECORDED, f"{sid}.json")
            if not os.path.exists(path):
                return None
            with open(path, encoding="utf-8") as fh:
                self.recorded[sid] = json.load(fh)
        return self.recorded[sid]

    def start(self, sid: str) -> dict:
        job = {"id": uuid.uuid4().hex[:12], "scenario": sid, "live": True, "status": "running",
               "started_at": time.time(), "finished_at": None, "steps": {}, "result": None, "error": None}

        def progress(step, status, detail=""):
            entry = job["steps"].setdefault(step, {"started_at": time.time()})
            entry.update(status=status, detail=detail)
            if status != "running":
                entry["finished_at"] = time.time()

        def work():
            try:
                job["result"] = serialize(SCENARIOS[sid]["run"](progress))
                job["status"] = "done"
            except Exception as exc:  # report, never crash the server
                job["error"], job["status"] = f"{type(exc).__name__}: {str(exc)[:300]}", "error"
            job["finished_at"] = time.time()

        with self.lock:
            cutoff = time.time() - 3600
            for jid in [j for j, v in self.jobs.items() if v["started_at"] < cutoff]:
                del self.jobs[jid]
            self.jobs[job["id"]] = job
        threading.Thread(target=work, daemon=True).start()
        return job

    def get(self, jid: str):
        return self.jobs.get(jid)


def record(sids=None) -> None:
    """Run scenarios live and save them as the recorded runs shipped with the demo."""
    os.makedirs(RECORDED, exist_ok=True)
    for sid in sids or SCENARIOS:
        steps = {}

        def progress(step, status, detail=""):
            entry = steps.setdefault(step, {"started_at": time.time()})
            entry.update(status=status, detail=detail)
            if status != "running":
                entry["finished_at"] = time.time()

        started = time.time()
        result = serialize(SCENARIOS[sid]["run"](progress))
        job = {"id": f"recorded-{sid}", "scenario": sid, "live": False, "status": "done",
               "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "started_at": started, "finished_at": time.time(), "steps": steps, "result": result, "error": None}
        with open(os.path.join(RECORDED, f"{sid}.json"), "w", encoding="utf-8") as fh:
            json.dump(job, fh, indent=1, ensure_ascii=False)
        print(f"recorded {sid}: {job['finished_at'] - started:.1f}s, ${result['totals']['cost_usd']:.5f}")
