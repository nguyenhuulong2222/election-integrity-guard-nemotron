"""Demo web server (stdlib http.server). API keys stay in this process; the browser never sees them.

  python -m nemotron_agent serve [--port 8000]

Decoy pages under /decoys/ are clearly labeled test pages for the misinformation hunter.
They carry a noindex meta tag, an X-Robots-Tag header, and robots.txt disallows them.
"""

from __future__ import annotations

import json
import os
import posixpath
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from . import demo

PKG = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(PKG, "web")
TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml", ".json": "application/json"}
ROBOTS = b"User-agent: *\nDisallow: /decoys/\n"
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; "
                               "img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'none'; "
                               "frame-ancestors 'none'",
}
JOBS = demo.Jobs()
LIMITS = demo.Limits()
MAX_BODY = 2048


class Handler(BaseHTTPRequestHandler):
    server_version = "eig-nemotron"
    sys_version = ""

    def log_message(self, fmt, *args):  # no query strings or bodies in logs
        print(f"{self.command} {urlsplit(self.path).path} -> {args[1] if len(args) > 1 else ''}")

    def send(self, status: int, body: bytes, ctype: str, extra: dict = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in {**SECURITY_HEADERS, **(extra or {})}.items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def static(self, rel: str, extra: dict = None) -> None:
        rel = posixpath.normpath(rel).lstrip("/")
        full = os.path.join(WEB, *rel.split("/"))
        if rel.startswith("..") or not full.startswith(WEB + os.sep) or not os.path.isfile(full):
            return self.send(404, b"not found\n", "text/plain; charset=utf-8")
        with open(full, "rb") as fh:
            body = fh.read()
        self.send(200, body, TYPES.get(os.path.splitext(full)[1], "application/octet-stream"), extra)

    def send_json(self, status: int, payload) -> None:
        self.send(status, json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8",
                  {"Cache-Control": "no-store"})

    def client_ip(self) -> str:
        forwarded = self.headers.get("X-Forwarded-For", "")  # set by Render's proxy
        return forwarded.split(",")[0].strip() or self.client_address[0]

    def do_POST(self):
        if urlsplit(self.path).path != "/api/run":
            return self.send_json(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            return self.send_json(413, {"error": "request too large"})
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self.send_json(400, {"error": "invalid JSON"})
        sid = body.get("scenario")
        if sid not in demo.SCENARIOS:
            return self.send_json(400, {"error": "unknown scenario"})
        if not body.get("live"):
            job = JOBS.recorded_job(sid)
            return self.send_json(200, job) if job else self.send_json(404, {"error": "no recorded run; try a live run"})
        if JOBS.running() >= demo.MAX_CONCURRENT:
            return self.send_json(429, {"error": "Two live runs are already in progress. Try again in a few seconds."})
        refusal = LIMITS.take(self.client_ip())
        if refusal:
            return self.send_json(429, {"error": refusal})
        return self.send_json(202, JOBS.start(sid))

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/scenarios":
            return self.send_json(200, {"scenarios": demo.scenario_list(), "routing": demo.routing(),
                                   "limits": {"daily": LIMITS.daily, "per_ip_hourly": LIMITS.per_ip}})
        if path.startswith("/api/jobs/"):
            job = JOBS.get(path[len("/api/jobs/"):])
            return self.send_json(200, job) if job else self.send_json(404, {"error": "unknown job"})
        if path == "/robots.txt":
            return self.send(200, ROBOTS, "text/plain; charset=utf-8")
        if path.startswith("/decoys/"):
            return self.static(path, {"X-Robots-Tag": "noindex, nofollow", "Cache-Control": "no-store",
                                      # decoys are self-contained pages with one inline <style> and no script
                                      "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; "
                                                                 "base-uri 'none'; form-action 'none'"})
        if path == "/healthz":
            return self.send(200, b"ok\n", "text/plain; charset=utf-8")
        if path in ("/", "/index.html"):
            return self.static("index.html")
        if path.startswith("/static/"):
            return self.static(path[len("/static/"):])
        return self.send(404, b"not found\n", "text/plain; charset=utf-8")

    do_HEAD = do_GET


def serve(port: int) -> None:
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving on http://0.0.0.0:{port}")
    httpd.serve_forever()
