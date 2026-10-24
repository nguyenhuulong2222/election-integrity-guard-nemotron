import json
import os
import threading
import unittest
import urllib.request

os.environ["EIG_USAGE_LOG"] = "off"

from nemotron_agent import hunter, multilingual  # noqa: E402
from nemotron_agent.llm import NemotronClient  # noqa: E402
from nemotron_agent.pages import visible_text  # noqa: E402
from nemotron_agent.schemas import ELECTION_FACTS, FACT_KEYS, validate  # noqa: E402
from nemotron_agent.tests.test_m1 import FakeTransport  # noqa: E402

CERT = multilingual.load_certified()
EN = visible_text(multilingual.load_pages("consistent")["en"])
QUOTES = {"election_day": "Tuesday, November 3, 2026", "polls_open": "7:00 am", "polls_close": "7:00 pm",
          "drop_box_close": "open until 7:00 pm", "mail_ballots_sent": "Tuesday, October 13, 2026",
          "service_centers_open": "Tuesday, October 20, 2026", "certification_date": "Tuesday, November 17, 2026",
          "polling_place_site": "Find your polling place: elections.kanaloacounty.example",
          "registration_site": "register.kanaloacounty.example", "phone": "(808) 555-0147"}


def facts(**overrides):
    out = {"language": "English",
           "facts": {k: {"value": CERT[k], "quote": QUOTES[k]} for k in FACT_KEYS},
           "drop_box_addresses": [{"value": a, "quote": a} for a in CERT["drop_box_addresses"]]}
    for key, (value, quote) in overrides.items():
        out["facts"][key] = {"value": value, "quote": quote}
    return out


class CompareTest(unittest.TestCase):
    def test_fixture_facts_are_schema_valid(self):
        self.assertEqual(validate(facts(), ELECTION_FACTS), [])

    def test_consistent_page_has_no_mismatch(self):
        self.assertEqual(multilingual.compare("en", facts(), EN, CERT), [])

    def test_equivalent_formats_are_not_mismatches(self):
        f = facts(polls_close=("7:00", "7:00 pm"), phone=("1-808-555-0147", "(808) 555-0147"),
                  polling_place_site=("https://elections.kanaloacounty.example/", "elections.kanaloacounty.example"))
        f["facts"]["polls_close"]["value"] = "19:00"
        self.assertEqual(multilingual.compare("en", f, EN, CERT), [])

    def test_wrong_value_with_real_quote_is_wrong(self):
        page = EN.replace("November 3", "November 4")
        rows = multilingual.compare("en", facts(election_day=("2026-11-04", "Tuesday, November 4, 2026")), page, CERT)
        self.assertEqual([(r["field"], r["kind"]) for r in rows], [("election_day", "wrong")])

    def test_quote_not_on_page_is_unverified_not_wrong(self):
        rows = multilingual.compare("en", facts(election_day=("2026-11-04", "Wednesday, November 4")), EN, CERT)
        self.assertEqual([(r["field"], r["kind"]) for r in rows], [("election_day", "unverified")])

    def test_lookalike_site_is_annotated(self):
        page = EN.replace("elections.kanaloacounty", "elections.kanaloa-county")
        rows = multilingual.compare("en", facts(polling_place_site=(
            "elections.kanaloa-county.example", "elections.kanaloa-county.example")), page, CERT)
        self.assertEqual(rows[0]["lookalike_of"], "kanaloacounty.example")

    def test_missing_fact(self):
        rows = multilingual.compare("en", facts(phone=("", "")), EN, CERT)
        self.assertEqual([(r["field"], r["kind"]) for r in rows], [("phone", "missing")])

    def test_scenarios_apply_and_bad_replacement_fails(self):
        drift = multilingual.load_pages("drift")
        self.assertIn("Nobyembre 4", drift["tl"])
        with self.assertRaises(ValueError):
            multilingual.apply_replacements({"en": [["no such text", "x"]]})


class MultilingualRunTest(unittest.TestCase):
    def test_no_explain_call_when_consistent(self):
        fake = FakeTransport(facts())
        out = multilingual.run({"en": multilingual.load_pages("consistent")["en"]}, NemotronClient(fake))
        self.assertEqual(out["mismatches"], [])
        self.assertEqual(len(fake.sent), 1)
        self.assertFalse(fake.sent[0]["thinking"])


class HunterTest(unittest.TestCase):
    def items(self):
        return [
            {"url": "https://www.example-state.gov/vote", "title": "State voting", "demo_decoy": False,
             "text": "Election Day is November 4, 2026. Find your polling place.", "source": "search"},
            {"url": "https://demo.test/decoys/x.html", "title": "", "demo_decoy": True, "source": "watchlist",
             "text": "Kanaloa County voters: Election Day is now Wednesday, November 4, 2026. "
                     "Find your polling place at elections.kanaloa-county.example. " * 3},
        ]

    def test_guard_never_accuses_pages_without_the_county(self):
        triage = {"items": [{"id": "r1", "about_county": True, "category": "misinformation", "reason": "x"},
                            {"id": "r2", "about_county": True, "category": "official", "reason": "y"}]}
        decoy_facts = facts(election_day=("2026-11-04", "Wednesday, November 4, 2026"))
        report = {"findings": [], "report_md": "## Summary"}
        fake = FakeTransport(triage, decoy_facts, report)
        out = hunter.run(NemotronClient(fake), queries=(), gathered=(self.items(), [], []))
        by_url = {it["url"]: it for it in out["items"]}
        self.assertEqual(by_url["https://www.example-state.gov/vote"]["category"], "unrelated")
        decoy = by_url["https://demo.test/decoys/x.html"]
        self.assertEqual(decoy["category"], "impersonation")  # "official" is reserved for official hosts
        self.assertEqual(decoy["lookalikes"], ["elections.kanaloa-county.example"])
        self.assertEqual([m["field"] for m in decoy["contradictions"]], ["election_day"])
        self.assertEqual(len(fake.sent), 3)  # triage, one extraction (only the county page), report

    def test_triage_that_skips_items_is_retried(self):
        partial = {"items": [{"id": "r1", "about_county": False, "category": "unrelated", "reason": "x"}]}
        full = {"items": partial["items"] + [{"id": "r2", "about_county": True, "category": "misinformation",
                                              "reason": "y"}]}
        fake = FakeTransport(partial, full, facts(), {"findings": [], "report_md": "r"})
        hunter.run(NemotronClient(fake), queries=(), gathered=(self.items(), [], []))
        self.assertEqual(len(fake.sent), 4)
        self.assertIn("skipped 1 of 2", fake.sent[1]["messages"][-1]["content"])

    def test_lookalike_hosts(self):
        self.assertEqual(hunter.lookalike_hosts("go to kanaloacounty.example or registro-kanaloacounty.example"),
                         ["registro-kanaloacounty.example"])


class ServerTest(unittest.TestCase):
    def test_decoys_are_noindex_and_disallowed(self):
        from http.server import ThreadingHTTPServer
        from nemotron_agent.server import Handler
        Handler.log_message = lambda *a: None
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{httpd.server_address[1]}"
        try:
            with urllib.request.urlopen(base + "/decoys/kanaloa-vote-update.html") as resp:
                body = resp.read().decode()
                self.assertEqual(resp.headers["X-Robots-Tag"], "noindex, nofollow")
            self.assertIn('<meta name="robots" content="noindex,nofollow">', body)
            self.assertIn(hunter.DECOY_BANNER, body)
            with urllib.request.urlopen(base + "/robots.txt") as resp:
                self.assertIn("Disallow: /decoys/", resp.read().decode())
        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_every_decoy_is_labeled(self):
        d = os.path.join(os.path.dirname(multilingual.PKG), "nemotron_agent", "web", "decoys")
        for name in os.listdir(d):
            with open(os.path.join(d, name), encoding="utf-8") as fh:
                html = fh.read()
            self.assertIn("noindex", html, name)
            self.assertGreaterEqual(html.count(hunter.DECOY_BANNER), 2, name)


if __name__ == "__main__":
    unittest.main()
