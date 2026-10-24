"""Tavily Search and Extract over REST (stdlib urllib). The key comes from TAVILY_API_KEY.

Each call is logged to the same usage log as the model calls (endpoint, latency, result
count, credits), never the key or the page contents.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from . import config
from .llm import CallRecord, _write_usage, load_env

TIMEOUT_S = 40.0


class TavilyError(RuntimeError):
    pass


def _post(path: str, body: dict, task: str) -> dict:
    load_env()
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        raise TavilyError("TAVILY_API_KEY is not set (put it in .env or the environment)")
    req = urllib.request.Request(config.TAVILY_URL + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            data = json.load(resp)
        error = None
    except urllib.error.HTTPError as exc:
        data, error = {}, f"HTTP {exc.code}: {exc.read()[:200].decode(errors='replace')}"
    except (urllib.error.URLError, TimeoutError) as exc:
        data, error = {}, f"{type(exc).__name__}: {exc}"
    latency = int((time.monotonic() - started) * 1000)
    rec = CallRecord(task, "tavily", "tavily" + path, 0, len(data.get("results", [])), 0, latency, 0.0,
                     error is None, 1, error)
    _write_usage(rec)
    if error:
        raise TavilyError(f"{task}: {error}")
    data["_record"] = rec
    return data


def search(query: str, max_results: int = 5) -> dict:
    """Basic-depth web search (1 API credit)."""
    return _post("/search", {"query": query, "max_results": max_results, "search_depth": "basic"},
                 task="tavily_search")


def extract(urls: list) -> dict:
    """Page text for up to 20 URLs (basic depth: 1 credit per 5 URLs). Plain text keeps lists and
    tables that the default markdown output dropped in our tests."""
    return _post("/extract", {"urls": urls[:20], "format": "text"}, task="tavily_extract")
