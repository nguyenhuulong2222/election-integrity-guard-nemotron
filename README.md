# Election Integrity Guard

**A supervised GitLab Duo agent workflow that stops bad merges from reaching an election website.**

**Live demo (fictional):** https://showcase-0b6166.gitlab.io (results: [/results.html](https://showcase-0b6166.gitlab.io/results.html), voter info: [/voter-info.html](https://showcase-0b6166.gitlab.io/voter-info.html))

> Built for the GitLab Transcend Hackathon (Path A, new code written in October 2026). The demo site, "Kanaloa County Elections", is **fictional**. Every county, candidate and number in this repository is invented.

## The problem

Election offices publish results and official voter information on ordinary websites. One bad merge can publish things that damage public trust within minutes:

- **Wrong numbers.** A typo or a bad export makes the vote totals impossible.
- **A fake link.** A polling-place lookup link is swapped to a lookalike domain.
- **An injected script.** A third-party script is added, or the Content Security Policy is quietly weakened.

The cause may be an honest mistake, a compromised account, or a malicious insider. Either way, the damage happens at publish time, and code review alone is easy to rush on election night.

## How it works

_Architecture diagram: coming in Phase 6._

1. **Deterministic gate.** A stdlib-only Python checker runs in CI on every merge request. It checks results arithmetic, official-link domains, scripts and assets, the CSP, and governance rules. It emits `BLOCK` / `WARN` / `PASS` as JSON and markdown, and it fails the pipeline on `BLOCK`.
2. **Duo agent review.** When the pipeline finishes, a GitLab Duo Agent Platform custom flow reads the MR diff and the checker report. It then:
   - posts a plain-language review (verdict, findings, risk, suggested fix)
   - applies an `integrity::block`, `integrity::warn` or `integrity::pass` label
   - opens a linked issue for each BLOCK finding
3. **Human release.** The agent **cannot** merge, approve or deploy. A code owner approves the MR, and the Pages deploy to `production` waits for that approval.
4. **Watch after release.** A scheduled job compares the live site with `main` and raises an alarm on drift.

**Autonomy level: Supervised.** The AI explains and recommends, the deterministic checker enforces, and a human decides.

## DevSecOps stages covered

| Stage | Covered by |
|---|---|
| Plan | Results-update and incident issue templates |
| Create | MR template, CODEOWNERS |
| Verify | `verify` job: lint and unit tests |
| Secure | `integrity` checker job, plus GitLab SAST and Secret Detection |
| Package | `package` job: site bundle and SHA-256 manifest |
| Release | Pages deploy from `main` to a protected `production` environment, after human approval |
| Configure | Policy-as-code in `config/`, plus the Duo flow config |
| Monitor | Scheduled drift check of the live site |
| Govern | Code-owner approval, required issue link, protected branch, agent with no merge rights |

_A full mapping table is coming in Phase 6._

## Repository layout

```
public/      fictional election site (static HTML, no framework)
results/     results.json and earlier updates
config/      allowlists, anomaly threshold, required CSP
checker/     deterministic integrity checker (Python 3, stdlib only)
scripts/     monitor / drift job
.gitlab/     CODEOWNERS, templates, Duo flow and agent definitions
docs/        settings checklist and architecture
```

## Run it locally

Requirements: Python 3.11+ and git. No third-party packages.

```bash
# Unit tests: rules, the four demo scenarios end to end, and the package and monitor scripts
python3 -m unittest discover -s checker/tests -t . -v

# Run the integrity checker against main, as the integrity CI job does
python3 -m checker --base origin/main --out-dir /tmp/eig --no-fail
cat /tmp/eig/eig-report.md

# Simulate an MR, including the "must reference an issue" rule
echo "Closes #2" > /tmp/mr.txt
python3 -m checker --base origin/main --mr-description-file /tmp/mr.txt --out-dir /tmp/eig

# Build and preview the site, as the package job does
python3 scripts/build_site.py
python3 -m http.server -d public 8000            # http://localhost:8000

# Check a live site for drift, as the monitor job does (use the local preview or the live demo)
python3 scripts/monitor_drift.py --url http://localhost:8000/ --out-dir /tmp/eig
git fetch origin && python3 scripts/monitor_drift.py --url https://showcase-0b6166.gitlab.io --main-ref origin/main --out-dir /tmp/eig
```

Checker exit codes:

| Code | Meaning |
|---|---|
| `0` | PASS or WARN |
| `1` | BLOCK |
| `2` | Configuration error |

### Integrity rules

| Area | Rules | Severity |
|---|---|---|
| Results arithmetic | Votes are non-negative integers; candidate votes sum to the contest total; precincts reporting ≤ total; ballots cast ≤ registered voters; turnout is 0–100% and matches the counts; a contest total is never above ballots cast | BLOCK |
| Anomalies, compared with the previous update | A vote-share swing larger than `config/policy.json → anomaly.max_share_swing_pp` (default 5 pp); vote counts or precincts going down; update sequence not increasing; candidate list changed | WARN |
| Official links | Must be HTTPS on an allowlisted domain (`config/allowlist.json`); lookalikes of official domains are blocked anywhere on the site (digit or homoglyph swaps, hyphens, extra words, punycode) | BLOCK |
| Scripts and assets | Third-party `<script>`, `<iframe>`, `<embed>` or `<object>` off the allowlist; inline `<script>`; inline `on*=` handlers; `javascript:` URLs | BLOCK |
| | `eval` / `new Function` / string timers; `innerHTML`-style sinks; third-party stylesheets | WARN |
| Security headers | CSP `<meta>` present on every page; required directives kept; no `'unsafe-inline'`, `*` or scheme wildcards; no widening against the MR base; `config/security-policy.json` never loosened | BLOCK |
| Governance | The MR must reference an issue; CODEOWNERS must cover `/results/` and `/config/`; changes to protected paths are noted for code-owner approval | BLOCK / INFO |

## Project settings

Some protections can only be set in the GitLab UI. See [`docs/ui-settings.md`](docs/ui-settings.md).

**Demo disclosure:** this is a solo project, so **"Prevent approval by author" is turned off** and the author approves their own MRs. In production, a separate election official is the required approver, and that setting stays on.

## License

[MIT](LICENSE) © 2026 Long Huu Nguyen
