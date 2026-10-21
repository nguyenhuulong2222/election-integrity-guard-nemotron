# Election Integrity Guard

**A supervised GitLab Duo agent workflow that stops bad merges from reaching an election website.**

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

_Commands are filled in as each phase lands._

```bash
# Requirements: Python 3.11+ (no third-party packages)
python3 -m unittest discover -s checker/tests        # unit tests (Phase 3)
python3 -m checker --base origin/main --head HEAD    # run the integrity checker (Phase 3)
python3 -m http.server -d public 8000                # preview the site (Phase 2)
```

## Project settings

Some protections can only be set in the GitLab UI. See [`docs/ui-settings.md`](docs/ui-settings.md).

**Demo disclosure:** this is a solo project, so **"Prevent approval by author" is turned off** and the author approves their own MRs. In production, a separate election official is the required approver, and that setting stays on.

## License

[MIT](LICENSE) © 2026 Long Huu Nguyen
