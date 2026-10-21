# CLAUDE.md: Election Integrity Guard

Context for any Claude Code session working on this repository.

## Working agreement

- Work in **gated phases** (0–6). At the end of each phase, STOP, report, and wait for the user to type **"chốt"**. Never start the next phase on your own.
- Gate report format:
  - what was done
  - files changed
  - pipeline status and link
  - UI clicks the user must make
  - risks
  - time left vs. the deadline

## Hard facts (from the official rules, do not change)

- **Hackathon:** GitLab Transcend Hackathon (Devpost). Solo developer.
- **Deadline:** Oct 27 2026 13:00 UTC (= 3:00am HST Tue Oct 27). **Internal deadline: Mon Oct 26 2026, 9:00pm HST.**
- **Repo:** https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43545862/showcase
  - Project ID `87857590`, default branch `main`
  - Remote `https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43545862/showcase.git`
- **Path A (Start Fresh):** all code is new, created on or after Oct 5 2026. Never copy code from other projects.
- **Autonomy level: Supervised.** The agent checks and recommends, and a human approves every release.
- **Must reasonably use the GitLab Duo Agent Platform** (agents, flows, or MCP). This is a pass/fail gate.
- **Required to qualify:**
  - public repo
  - MIT `LICENSE`
  - visible CI/CD pipeline history
  - run instructions
  - English materials
- **Video:** under 3 minutes, on YouTube, no copyrighted music. The user records it, and Claude writes the script (target < 2:45).
- **Judging (equal weight):** Technological Implementation, Design, Potential Impact, Innovation, Presentation.
- **Secondary target:** the "Most Stages Covered" prize (plan, create, verify, package, secure, release, configure, monitor, govern).

## Engineering invariants

1. **No invented APIs or schemas.** Before writing any Duo Agent Platform config, read the docs.gitlab.com page, then quote its URL and the schema followed. If the docs are unclear, stop and ask.
2. **Deterministic checks first, AI on top.** All integrity rules live in a plain Python 3 checker (stdlib only). The Duo agent explains and reasons about the checker output and never replaces the gate.
3. **Supervised:**
   - The agent may comment, label and open issues.
   - It may NEVER merge, approve or deploy.
   - Release requires a human approval enforced by GitLab settings (see `docs/ui-settings.md`).
4. **No secrets in the repo.** Tokens go in masked and protected CI/CD variables. Never print tokens.
5. **Clearly fictional data.** No real candidates, parties or county names. Every page carries a "Fictional demo data" banner.
6. **Small, reviewable conventional commits.** Never `git push --force` or `push -uf`.
7. **Ship over polish.** Propose cutting anything over about 2 hours that isn't required to qualify.

## Phase 0 decisions (approved 2026-10-21)

**Duo mechanism: a custom flow, in the AI Catalog, started by a project trigger.**
- Flow YAML uses flow registry v1 with `environment: ambient` and `coding_environment: none`.
- Source of truth: `.gitlab/duo/flows/integrity-review.yml`, pasted into AI > Flows. The repo-path configuration source is behind the disabled `ai_catalog_create_third_party_flows` flag.
- Docs:
  - https://docs.gitlab.com/user/duo_agent_platform/flows/custom_flows_schema/
  - https://gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/-/blob/main/docs/flow_registry/v1.md
- Custom flows reject:
  - `name` / `description` / `product_group` at the top level
  - `model` in prompts
  - `response_schema_*`
  - `stop` in `params`

**Triggers:**
- Main trigger: **Pipeline events** (Passed, Failed). The goal is the full pipeline webhook payload. The flow must exit early for pipelines that aren't MR pipelines (`main`, schedules).
- Manual re-run: **Mention**.
- Doc: https://docs.gitlab.com/user/duo_agent_platform/triggers/

**Tools:**
- `get_merge_request`, `list_merge_request_diffs`, `get_job_logs`, `gitlab_api_get` (read-only GET, used for the artifact)
- `create_merge_request_note`, `update_merge_request` (`add_labels` is confirmed in the tool source `duo_workflow_service/tools/merge_request.py`, not in the docs)
- `create_issue`
- No merge, approve or deploy tool.

**Tier:** assume Premium or Ultimate. The user confirms the AI menu before Phase 3.

**Approvals:** solo approver, so **"Prevent approval by author" is OFF**. Document this in README and `docs/ui-settings.md`: "in production a separate election official approves".

**Cuts and keeps:**
- **MCP: cut.**
- **results-triage flow: cut** unless Phase 4 finishes early.
- **Keep** the "Integrity Advisor" custom agent (about 15 min, at the end of Phase 4).

**Fallbacks:**
- **Monitor:** if `EIG_BOT_TOKEN` (project access token) isn't available on our tier, the monitor job must **FAIL the scheduled pipeline** with the drift report instead of opening an issue.
- **Labels:** the planned CI label fallback is **infeasible**, because a Developer can't create CI/CD variables, so there's no token. The replacement is a Code Quality report (`eig-codequality.json`), which shows BLOCK and WARN findings in the MR widget on all tiers.

**Pages:** GitLab Pages has no custom-headers support. The CSP is a `<meta http-equiv>` tag enforced by the checker. HSTS isn't controllable on `*.gitlab.io`, so the monitor job records the live headers instead.

## Branch protection sequencing (see docs/ui-settings.md)

1. **Phases 1–4:** `main` is protected, but Maintainers can push directly. Code-owner approval is **off**, because it denies direct pushes that touch code-owned paths.
2. **After Phase 3:** turn on "Pipelines must succeed".
3. **Before Phase 5:** set push = **No one** and code-owner approval **ON**. From then on, every change goes through an MR.

## Role blocker and Plan B (2026-10-21)

**Blocker.** The user's role is **Developer** (access_level 30) on both the project and the group, and Developer is not enough for the Duo work:
- Creating, enabling or triggering a custom flow or custom agent needs Maintainer or Owner.
- So do branch rules, approval rules, protected environments and project access tokens.

**Status.** Maintainer was requested on issue #1 (note 4060904922, mentions contributor-success), and the user is also asking on Discord. Re-check `access_level` at every gate:

```
glab api projects/87857590/members/all/43545862
```

**What still works as a Developer:**
- CI pipelines, the checker, the Pages deploy (`main` allows Developer push and merge), pipeline schedules
- labels, MRs, issues
- running flows that someone else has already enabled

**Plan B, if Maintainer isn't granted:**
1. Build and publish the flow from a personal project where the user is Owner, as a **Public** AI Catalog item. Enabling and triggering it in the showcase project still needs a Maintainer, so this only partly helps.
2. Run the flow from the VS Code GitLab flow builder (Developer can run), and record that for the demo.
3. Use GitLab's built-in Duo code review on the MRs, plus the deterministic checker posting its own MR comment from CI. This is weaker on the Duo gate, so state the limitation honestly in the README.

## Phase 3 implementation notes

**Checker:** `python3 -m checker`, stdlib only.
- Entry point and orchestration: `checker/engine.py`.
- Rules, with IDs in the README table:
  - `rules_results.py`
  - `rules_site.py`
  - `rules_governance.py`
- Output: `eig-report.json` and `eig-report.md`, also printed to the job log between `EIG-REPORT-JSON-BEGIN/END` markers so the Duo flow can read it with `get_job_logs`.
- Exit code 1 on BLOCK.

**CI:** `.gitlab-ci.yml`, with stages verify, integrity, secure, package, release, monitor.
- SAST and Secret Detection templates are moved to the `secure` stage, with `AST_ENABLE_MR_PIPELINES=true`.
- Release is the `release-pages` job (`pages: true`, `when: manual`, main only). A human presses Run. This replaces protected-environment approval, which needs Maintainer.
- Monitor runs in every scheduled pipeline (no variables, because Developers can't set pipeline variables here). It fails on drift, and opens an issue only if `EIG_BOT_TOKEN` exists.

## Phase status

- [x] Phase 0: recon and plan
- [x] Phase 1: repo foundation (approved, pushed)
- [x] Phase 2: demo election site (approved, pushed)
- [x] Phase 3: checker and CI (approved; pipelines green; site live at https://showcase-0b6166.gitlab.io; monitor schedule 4504749)
- [x] Phase 4: Duo flow and agent (approved; repo parts done; UI parts blocked on Maintainer, see docs/duo-setup.md). **Plan B cutoff: Thu Oct 22, 6pm HST.**
- [x] Phase 5: demo scenario MRs (approved). They're left open on purpose:
  - !1 arithmetic error → BLOCK (issue #2)
  - !2 lookalike polling link → BLOCK (issue #3)
  - !3 injected script and weakened CSP → BLOCK (issue #4)
  - !4 clean update 4 → PASS (issue #5)

  **Never merge them.** The user approves and merges !4 on camera, then presses Run on `release-pages`. Once the flow is enabled, re-run each MR pipeline (or mention the flow) to get the agent reviews.
- [ ] Phase 6: submission package. Drafts are done: README, `docs/devpost.md`, `docs/video-script.md` (versions A and B). Nothing is recorded yet. Fill the `<!-- FILL -->` and `<!-- STATUS -->` markers once the flow status is known.
