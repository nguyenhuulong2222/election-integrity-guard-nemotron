import json
import os
import threading
import unittest
import urllib.error
import urllib.request

os.environ["EIG_USAGE_LOG"] = "off"

from nemotron_agent import demo  # noqa: E402
from nemotron_agent.llm import CallRecord  # noqa: E402


class LimitsTest(unittest.TestCase):
    def test_per_ip_and_daily_caps(self):
        lim = demo.Limits(daily=3, per_ip=2)
        t = 1_800_000_000.0
        self.assertIsNone(lim.take("a", t))
        self.assertIsNone(lim.take("a", t + 1))
        self.assertIn("per hour", lim.take("a", t + 2))
        self.assertIsNone(lim.take("a", t + 3601))  # the hour window slid
        self.assertIn("daily limit", lim.take("b", t + 3602))

    def test_serialize_totals_split_models_and_tavily(self):
        calls = [CallRecord("t", "reasoning", "m", 100, 50, 10, 900, 0.001, True, 1),
                 CallRecord("s", "tavily", "tavily/search", 0, 5, 0, 400, 0.0, True, 1)]
        out = demo.serialize({"calls": calls})
        self.assertEqual(out["totals"]["model_calls"], 1)
        self.assertEqual(out["totals"]["tavily_calls"], 1)
        json.dumps(out)


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from http.server import ThreadingHTTPServer
        from nemotron_agent.server import Handler
        Handler.log_message = lambda *a: None
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def post(self, body):
        req = urllib.request.Request(self.base + "/api/run", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.load(resp)
        except urllib.error.HTTPError as exc:
            return exc.code, json.load(exc)

    def test_scenarios_and_recorded_replay_need_no_keys(self):
        with urllib.request.urlopen(self.base + "/api/scenarios") as resp:
            data = json.load(resp)
        self.assertEqual({r["role"] for r in data["routing"]}, {"FAST", "REASONING", "REPORT"})
        status, job = self.post({"scenario": "tamper"})
        self.assertEqual(status, 200)
        self.assertEqual(job["result"]["decision"]["action"], "ROLLBACK")
        self.assertFalse(job["live"])

    def test_unknown_scenario_and_big_body_rejected(self):
        self.assertEqual(self.post({"scenario": "nope"})[0], 400)
        self.assertEqual(self.post({"scenario": "x" * 3000})[0], 413)

    def test_index_has_strict_csp_and_no_keys(self):
        with urllib.request.urlopen(self.base + "/") as resp:
            csp = resp.headers["Content-Security-Policy"]
            html = resp.read().decode()
        self.assertIn("script-src 'self'", csp)
        self.assertNotIn("unsafe", csp)
        self.assertIn("Fictional demo data", html)
        for name in ("app.js", "index.html", "styles.css"):
            with open(os.path.join(demo.PKG, "web", name), encoding="utf-8") as fh:
                text = fh.read()
            self.assertNotIn("NEBIUS_API_KEY", text)
            self.assertNotIn("TAVILY_API_KEY", text)


if __name__ == "__main__":
    unittest.main()
