"""Monitor step: compare the live Pages site with what main says should be published.

Usage: python3 scripts/monitor_drift.py [--url URL] [--main-ref REF] [--out-dir DIR]

1. Fetch the live manifest.json to learn which commit is deployed.
2. Check that commit is part of main's history (it must have gone through review).
3. Rebuild the expected files from that commit and compare SHA-256 hashes with the live files.
4. Record the live security headers (HSTS cannot be set from the repository on GitLab Pages).

Drift opens an incident issue when EIG_BOT_TOKEN is set, and always fails the job
(exit 1) so the scheduled pipeline turns red. Exit 0 means the live site matches.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_files import MANIFEST, sha256, site_files  # noqa: E402

UA = "election-integrity-guard-monitor/1.0"
HEADERS_OF_INTEREST = ("strict-transport-security", "content-security-policy", "x-content-type-options",
                       "content-type", "cache-control")


def fetch(url: str, timeout: float = 20.0):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.read(), {k.lower(): v for k, v in res.headers.items()}
    except urllib.error.HTTPError as exc:
        return exc.code, b"", {}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, str(exc).encode(), {}


def is_ancestor(root: str, commit: str, ref: str) -> bool:
    res = subprocess.run(["git", "merge-base", "--is-ancestor", commit, ref], cwd=root, capture_output=True)
    return res.returncode == 0


def rev(root: str, ref: str):
    res = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref + "^{commit}"], cwd=root,
                         capture_output=True, text=True)
    return res.stdout.strip() if res.returncode == 0 else None


def check(base_url: str, root: str, main_ref: str) -> dict:
    base_url = base_url.rstrip("/") + "/"
    problems, notes = [], []
    main_sha = rev(root, main_ref)

    status, body, headers = fetch(urllib.parse.urljoin(base_url, MANIFEST))
    deployed = None
    if status != 200:
        problems.append(f"Live manifest.json is unavailable (HTTP {status}). The site is down or was replaced.")
    else:
        try:
            deployed = json.loads(body.decode("utf-8")).get("commit")
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            problems.append("Live manifest.json is not valid JSON.")

    compare_ref = None
    if deployed:
        if rev(root, deployed) is None:
            problems.append(f"Deployed commit {deployed[:12]} does not exist in this repository.")
        elif main_sha and not is_ancestor(root, deployed, main_sha):
            problems.append(f"Deployed commit {deployed[:12]} is not part of main's history: it never went "
                            "through the reviewed merge path.")
        else:
            compare_ref = deployed
            if main_sha and deployed != main_sha:
                notes.append(f"main ({main_sha[:12]}) has changes that are not deployed yet; the live site is "
                             f"at {deployed[:12]}. This is expected while a release waits for approval.")

    mismatched, checked = [], 0
    if compare_ref:
        for path, data in sorted(site_files(root, compare_ref).items()):
            status, live, _ = fetch(urllib.parse.urljoin(base_url, path))
            checked += 1
            if status != 200:
                mismatched.append({"path": path, "problem": f"HTTP {status}"})
            elif sha256(live) != sha256(data):
                mismatched.append({"path": path, "problem": "content differs",
                                   "expected_sha256": sha256(data), "live_sha256": sha256(live)})
        if mismatched:
            problems.append(f"{len(mismatched)} of {checked} live files differ from commit {compare_ref[:12]}.")

    _, _, index_headers = fetch(base_url)
    live_headers = {k: index_headers.get(k) for k in HEADERS_OF_INTEREST}
    if not live_headers.get("strict-transport-security"):
        notes.append("No Strict-Transport-Security header on the live site. GitLab Pages does not let the "
                     "repository set it; recorded for the record, not a failure.")

    return {
        "tool": "election-integrity-guard-monitor",
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "site": base_url,
        "main_commit": main_sha,
        "deployed_commit": deployed,
        "files_checked": checked,
        "drift": bool(problems),
        "problems": problems,
        "mismatched_files": mismatched,
        "notes": notes,
        "live_headers": live_headers,
    }


def to_markdown(r: dict) -> str:
    lines = ["## Live site drift check", "",
             f"**{'DRIFT DETECTED' if r['drift'] else 'No drift'}** on {r['site']} at {r['checked_at']}.", "",
             f"- Deployed commit: `{(r['deployed_commit'] or 'unknown')[:12]}`",
             f"- main: `{(r['main_commit'] or 'unknown')[:12]}`",
             f"- Files compared: {r['files_checked']}", ""]
    if r["problems"]:
        lines += ["### Problems", ""] + [f"- {p}" for p in r["problems"]] + [""]
    if r["mismatched_files"]:
        lines += ["| File | Problem |", "|---|---|"]
        lines += [f"| `{m['path']}` | {m['problem']} |" for m in r["mismatched_files"]] + [""]
    if r["notes"]:
        lines += ["### Notes", ""] + [f"- {n}" for n in r["notes"]] + [""]
    lines += ["### Live response headers", ""]
    lines += [f"- `{k}`: {v if v else '(not set)'}" for k, v in r["live_headers"].items()] + [""]
    return "\n".join(lines)


def open_incident(report_md: str) -> str:
    """Open (or reuse) an integrity-incident issue. Requires EIG_BOT_TOKEN; never prints it."""
    api, project = os.environ["CI_API_V4_URL"], os.environ["CI_PROJECT_ID"]
    token = os.environ["EIG_BOT_TOKEN"]
    title = "Live site drift detected"
    headers = {"PRIVATE-TOKEN": token, "User-Agent": UA}

    query = urllib.parse.urlencode({"state": "opened", "labels": "integrity-incident", "search": title})
    req = urllib.request.Request(f"{api}/projects/{project}/issues?{query}", headers=headers)
    with urllib.request.urlopen(req, timeout=20) as res:
        existing = [i for i in json.load(res) if i.get("title") == title]
    if existing:
        iid = existing[0]["iid"]
        data = urllib.parse.urlencode({"body": report_md}).encode()
        req = urllib.request.Request(f"{api}/projects/{project}/issues/{iid}/notes", data=data, headers=headers)
        urllib.request.urlopen(req, timeout=20).close()
        return existing[0]["web_url"]

    description = (report_md + "\n\n_Opened automatically by the scheduled monitor job "
                   f"({os.environ.get('CI_JOB_URL', 'local run')}). Fictional demo site._")
    data = urllib.parse.urlencode({"title": title, "description": description,
                                   "labels": "integrity-incident"}).encode()
    req = urllib.request.Request(f"{api}/projects/{project}/issues", data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.load(res)["web_url"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default=os.environ.get("CI_PAGES_URL"), help="live site (default: $CI_PAGES_URL)")
    parser.add_argument("--root", default=".")
    parser.add_argument("--main-ref", default="HEAD", help="the reviewed branch tip to trust (default: HEAD)")
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args(argv)
    if not args.url:
        print("error: no site URL (pass --url or set CI_PAGES_URL)", file=sys.stderr)
        return 2

    report = check(args.url, os.path.abspath(args.root), args.main_ref)
    md = to_markdown(report)
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "drift-report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    with open(os.path.join(args.out_dir, "drift-report.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)

    if not report["drift"]:
        return 0
    if os.environ.get("EIG_BOT_TOKEN"):
        try:
            print(f"Incident issue: {open_incident(md)}")
        except (urllib.error.URLError, KeyError, OSError) as exc:
            print(f"Could not open incident issue ({type(exc).__name__}); failing the job instead.")
    else:
        print("EIG_BOT_TOKEN is not set, so no incident issue was opened. "
              "Failing the scheduled pipeline so the drift is visible.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
