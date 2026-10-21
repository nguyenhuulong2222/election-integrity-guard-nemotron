"""Package + monitor scripts against a local HTTP server serving a temp copy of the site."""

import contextlib
import functools
import http.server
import io
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

from checker.tests.helpers import REPO, ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_site  # noqa: E402
import monitor_drift  # noqa: E402


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@unittest.skipUnless(shutil.which("git"), "git is required")
class MonitorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="eig-mon-")
        for name in ("public", "results"):
            shutil.copytree(os.path.join(REPO, name), os.path.join(self.tmp, name),
                            ignore=shutil.ignore_patterns("data", "manifest.json"))
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t.example",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t.example")
        for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "site"]):
            subprocess.run(["git", *args], cwd=self.tmp, check=True, capture_output=True, env=env)
        os.environ.pop("CI_COMMIT_SHA", None)
        with contextlib.redirect_stdout(io.StringIO()):
            build_site.main(["--root", self.tmp])
        handler = functools.partial(_Quiet, directory=os.path.join(self.tmp, "public"))
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_monitor(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return monitor_drift.main(["--url", self.url, "--root", self.tmp, "--out-dir", self.tmp])

    def test_clean_site_has_no_drift(self):
        os.environ.pop("EIG_BOT_TOKEN", None)
        self.assertEqual(self.run_monitor(), 0)

    def test_tampered_file_is_drift(self):
        os.environ.pop("EIG_BOT_TOKEN", None)
        with open(os.path.join(self.tmp, "public", "data", "results.json"), "a", encoding="utf-8") as fh:
            fh.write(" ")
        self.assertEqual(self.run_monitor(), 1)
        report = monitor_drift.check(self.url, self.tmp, "HEAD")
        self.assertEqual([m["path"] for m in report["mismatched_files"]], ["data/results.json"])

    def test_non_http_urls_are_refused(self):
        status, body, _ = monitor_drift.fetch("file:///etc/hosts")
        self.assertIsNone(status)
        self.assertIn(b"only http and https", body)

    def test_missing_manifest_is_drift(self):
        os.remove(os.path.join(self.tmp, "public", "manifest.json"))
        self.assertTrue(monitor_drift.check(self.url, self.tmp, "HEAD")["drift"])


if __name__ == "__main__":
    unittest.main()
