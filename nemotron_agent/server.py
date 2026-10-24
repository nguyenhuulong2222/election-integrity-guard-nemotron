"""Demo web server (stdlib http.server). API keys stay in this process; the browser never sees them.

  python -m nemotron_agent serve [--port 8000]

Decoy pages under /decoys/ are clearly labeled test pages for the misinformation hunter.
They carry a noindex meta tag, an X-Robots-Tag header, and robots.txt disallows them.
"""

from __future__ import annotations

import os
import posixpath
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

PKG = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(PKG, "web")
TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml", ".json": "application/json"}
ROBOTS = b"User-agent: *\nDisallow: /decoys/\n"
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
}


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

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/robots.txt":
            return self.send(200, ROBOTS, "text/plain; charset=utf-8")
        if path.startswith("/decoys/"):
            return self.static(path, {"X-Robots-Tag": "noindex, nofollow", "Cache-Control": "no-store"})
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
