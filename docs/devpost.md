# Devpost submission draft: Election Integrity Guard

> DRAFT. Fill in each `<!-- FILL: ... -->` before submitting. Every claim below can be checked in the repository or its pipelines.

**Project name:** Election Integrity Guard

**Tagline (≤ 200 chars):** A supervised GitLab Duo workflow that blocks bad merges to election websites (wrong totals, lookalike polling links, injected scripts), explains them in plain English, and leaves release to a human.

**Track / path:** Path A (Start Fresh): all code was written in October 2026 for this hackathon.
**Autonomy level:** Supervised. The agent checks and recommends; a human approves every release.

**Links:**
- Repository: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43545862/showcase (MIT licensed)
- Live demo (fictional): https://showcase-0b6166.gitlab.io
- Video: <!-- FILL: YouTube URL -->

**Image gallery** (upload in this order; all captured logged out, all data fictional):
1. [`screenshots/cover.png`](screenshots/cover.png): cover, 1500×1000
2. [`screenshots/mr2-duo-review.png`](screenshots/mr2-duo-review.png): Duo review on !2, lookalike domain BLOCK
3. [`screenshots/mr3-duo-review.png`](screenshots/mr3-duo-review.png): Duo review on !3, five blockers explained (script tag and weakened CSP)
4. [`screenshots/mr3-code-quality-report.png`](screenshots/mr3-code-quality-report.png): five blockers on !3 in Code Quality
5. [`screenshots/mr1-duo-review.png`](screenshots/mr1-duo-review.png): arithmetic BLOCK on !1
6. [`screenshots/mr4-duo-review.png`](screenshots/mr4-duo-review.png): PASS review on !4
7. [`screenshots/mr3-pipeline.png`](screenshots/mr3-pipeline.png): `integrity` fails while the security scans pass
8. [`screenshots/site-results.png`](screenshots/site-results.png): the fictional results page

---

## Inspiration

Election offices increasingly publish results and voter information from a Git repository through a static site. That's good engineering, but it means **a single merge can change what voters see on election night**. Three failure modes worried us:

1. **Impossible numbers.** A hand-edited "recount" bumps one candidate's votes and forgets the contest total.
2. **A fake official link.** "Find your polling place" points at `kanaloa-county.example` instead of `kanaloacounty.example`. One hyphen, invisible in a diff.
3. **An injected script.** A harmless-sounding "analytics tag" adds third-party JavaScript and loosens the Content Security Policy to let it run.

Human review alone misses these under deadline pressure. Fully autonomous AI is the wrong answer too: nobody should let a model decide what an election website says. So we built the middle path.

## What it does

Election Integrity Guard reviews **every merge request** to an election website **after the code is written**. It works in three layers:

- **A deterministic gate (CI).** A stdlib-only Python checker runs in every MR pipeline. It checks:
  - **results arithmetic:** sums, precincts, turnout, ballots versus registered voters
  - **anomalies between updates:** vote-share swings above a configurable threshold, counts going down
  - **official links:** domain allowlist plus lookalike detection (homoglyphs, punycode, hyphens, extra words)
  - **scripts and assets:** third-party scripts and iframes, inline scripts and handlers, `eval`
  - **the CSP:** present, not widened against the MR base, and its own policy file never loosened
  - **governance:** the MR must close an issue; CODEOWNERS must cover results and policy

  It returns **BLOCK / WARN / PASS** as JSON, Markdown and a Code Quality report, and fails the pipeline on BLOCK.
- **A GitLab Duo Agent Platform custom flow.** When an MR pipeline finishes, a *Pipeline events* trigger starts the flow. It reads the checker report and the MR diff, then posts **one plain-language review** for an election official: the verdict, what changed, why it matters to voters, and the suggested fix. It applies an `integrity::block|warn|pass` label and opens an incident issue for BLOCK findings. Mentioning the flow asks for a fresh review. An optional **Integrity Advisor** custom agent answers follow-up questions in Duo Chat.
- **A human release, then monitoring.** The agent has no merge, approve or deploy tool, and its service account can't merge to protected `main`. A person merges and presses **Run** on the Pages release job. A scheduled pipeline then compares every live file's SHA-256 hash with the reviewed commit, and fails loudly on drift.

In the demo, four MRs against the fictional "Kanaloa County Elections" site show it working: an arithmetic error, a lookalike polling-place link, and an injected script with a weakened CSP are **blocked**, and a clean results update **passes**.

## How we built it

- **Deterministic first, AI on top.** All integrity rules are plain Python 3 with no dependencies, plus **64 unit tests**: every rule, the four demo scenarios end to end, and the package and monitor scripts against a local server. The tests use a frozen fixture snapshot, so they test the checker rather than the MR being checked.
- **Duo flow from the official schema.** The flow is a flow registry v1 YAML: `environment: ambient`, `coding_environment: none`, one `AgentComponent` with a locally defined prompt. We kept to the custom-flow restrictions in GitLab's docs (no `model`, no response schemas, no top-level name) and used only documented tools: `get_merge_request`, `list_merge_request_diffs`, `get_job_logs`, `gitlab_api_get`, `create_merge_request_note`, `update_merge_request` (labels only) and `create_issue`. The flow:
  - skips any pipeline that isn't a finished MR pipeline
  - won't post twice for the same pipeline: a visible `EIG Duo review · pipeline <id>` marker, because GitLab rejects HTML comments in flow prompts
  - treats MR text as untrusted data, not instructions
- **The checker reaches the agent two ways.** The report is a job artifact and is also printed into the job log, so the flow can read it with either `gitlab_api_get` or `get_job_logs`.
- **The pipeline covers the whole lifecycle:**
  - **verify:** unit tests
  - **integrity:** the deterministic checker
  - **secure:** GitLab SAST and Secret Detection, running even when the gate blocks
  - **package:** site bundle plus SHA-256 manifest
  - **release:** a manual Pages deploy
  - **monitor:** a scheduled drift check
- **The site** is static HTML, CSS and one JS file, with no framework. It has a strict meta CSP (`default-src 'none'`), renders only through `textContent`, meets WCAG AA contrast in light and dark mode, and carries a "Fictional demo data" banner on every page.

## Stages covered

| Stage | Coverage |
|---|---|
| Plan | Issue templates; every MR must close an issue |
| Create | MR template, CODEOWNERS |
| Verify | `verify` job, 64 unit tests |
| Secure | Integrity checker, SAST, Secret Detection |
| Package | SHA-256 site manifest |
| Release | Manual, human-run Pages deploy from `main` |
| Configure | Policy-as-code allowlists, threshold and CSP, plus the Duo flow config |
| Monitor | Scheduled live-site drift check |
| Govern | Issue link, CODEOWNERS, labels and review as an audit trail, an agent without merge rights |

## Challenges we ran into

- **Our hackathon role was a "Developer+" custom role, not Maintainer.**
  - It can create, enable and trigger Duo flows and agents, but not change protected branches, protected environments or project access tokens.
  - We redesigned around it: a manual release job as the human gate, a scheduled pipeline that needs no variables, and a Code Quality report so findings appear in the MR widget with no token.
  - We documented every setting that should be on in production. The Duo flow fires on every finished MR pipeline (Pipeline events trigger, filtered to MR pipelines).
- **GitLab's flow security validation.** Our first flow was rejected with "Flow configuration failed security validation". The cause was an HTML-comment marker in the prompt. We found the check in the Duo Workflow Service source, moved to a visible marker, and now run GitLab's own prompt sanitizers locally before every flow change.
- **GitLab Pages can't set response headers.** The CSP ships as a `<meta>` tag that the checker enforces, and we're upfront that `frame-ancestors` and HSTS can't be enforced this way.
- **Our own pipeline caught our own bug.** The first demo MR pipelines failed in `verify`, because the unit tests read the live data that the MR was changing. We moved the tests to a frozen fixture and made security scans run even when the gate blocks. Both fixes are visible in the pipeline history.

## Accomplishments we're proud of

- Lookalike-domain detection that catches `kanaloa-county`, `kanal0acounty`, a Cyrillic "а", punycode and `kanaloacounty.example.evil.test`, without flagging unrelated domains.
- A **CSP regression check** against the MR base. A change that only *adds* a host to `script-src` is caught, even when the page still "has a CSP".
- A clear separation of duties: **code enforces, AI explains, a human decides**, with every step visible in GitLab.

## What we learned

- The GitLab Duo Agent Platform is most useful when it is given **structured, deterministic evidence** to explain, rather than asked to be the judge.
- In a supervised workflow, the important design work is in what the agent *can't* do: its toolset, its service account's role, and branch protection.

## What's next

- Serve the CSP as a real header (CDN) and add `frame-ancestors` and HSTS checks.
- Signed results exports: verify a tabulation-system signature over `results.json` before it can merge.
- Multi-county allowlists, and a Duo flow that triages new "results update" issues into a checklist.

## Built with

GitLab Duo Agent Platform (custom flow, triggers, custom agent) · GitLab CI/CD · GitLab Pages · GitLab SAST · GitLab Secret Detection · Code Quality reports · Python 3 (standard library only) · HTML · CSS · JavaScript · Mermaid
