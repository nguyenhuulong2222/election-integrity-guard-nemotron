# GitLab UI settings checklist

Project: `gitlab-ai-hackathon/transcend-october-2026/43545862/showcase` (ID `87857590`)

Live Pages site: **https://showcase-0b6166.gitlab.io** (the `production` environment URL, and `$CI_PAGES_URL` in CI). Deploy > Pages is hidden for the Developer role; read the URL from Operate > Environments > production, or from the `release-pages` job log.

Some protections can only be set in the GitLab UI. Each item says which phase needs it.

> **Role (updated 2026-10-21).** Maintainer will not be granted (issue #1, note 4061769259). The owner's custom role **Developer+** can create, enable and trigger flows and agents, manage MR approval settings and merge checks, and edit CI/CD variables. It **cannot** change protected branches, protected environments or project access tokens. Items still marked **(blocked: needs Maintainer)** may now be possible; the flow, trigger, approval and merge-check items are covered by Developer+.

## Phase 1: now

- [x] **Visibility: Public.** Settings > General > Visibility, project features, permissions > Project visibility = **Public**. _(Already Public as of 2026-10-21.)_
- [ ] **Protected branch `main` (temporary settings).** Settings > Repository > Branch rules > `main`: **(blocked: needs Maintainer)**
  - Allowed to merge: **Maintainers**
  - Allowed to push and merge: **Maintainers** _(temporary, so Phases 2–4 can push directly)_
  - Allowed to force push: **off**
  - Code owner approval: **off for now.** With it on, GitLab *denies direct pushes to the protected branch when a CODEOWNERS rule matches* ([docs](https://docs.gitlab.com/user/project/repository/branches/protected/#require-code-owner-approval)), and Phases 2–4 push directly to code-owned paths. It is switched on before Phase 5.
- [ ] **Merge request approvals.** Settings > Merge requests > Merge request approvals:
  - [x] Approval rule "Election official": **1** approval required, approver = the owner. _(Created with the API on 2026-10-22, rule 89100755.)_
  - [ ] Approval settings: **UI only**, because the REST API returns 403 for this role.
  - Approval settings:
    - **Prevent approval by author: OFF** (demo only, see below)
    - Prevent approvals by users who add commits: OFF (demo only)
    - Remove all approvals when commits are added: **ON**
- [ ] **Merge checks.** Settings > Merge requests: **All threads must be resolved: ON**. **UI only:** the REST API returns 403 for this role.
- [x] **Pages.** Already turned on (API `pages_access_level: enabled`). The first deploy happens in Phase 3.

## After Phase 3 (once CI exists)

- [ ] **Merge checks.** Settings > Merge requests: **Pipelines must succeed: ON**. **UI only:** the REST API returns 403. **Required for the video:** without it, !1 to !3 are mergeable.

## Before Phase 5 (demo MRs)

- [ ] **Protected branch `main` (final settings).** Settings > Repository > Branch rules > `main`: **(blocked: needs Maintainer)**
  - Allowed to push and merge: **No one**, so every demo change goes through an MR
  - **Code owner approval: ON**

> **Why "Prevent approval by author" is off.** This is a one-person hackathon project, so the author is also the only approver. In production, a **separate election official** is the required approver, this setting stays **ON**, and the Duo service account is never an eligible approver.

## Phase 3: CI and release

- [ ] **Protected environment `production`.** Settings > CI/CD > Protected environments: allowed to deploy = Maintainers, **required approvals = 1**. _(Premium or Ultimate. Same solo-author caveat as above.)_ **(blocked: needs Maintainer)**
- [ ] **CI/CD variable `EIG_BOT_TOKEN`.** Create a project access token (Settings > Access tokens: role Reporter, scope `api`, expiry ≤ Oct 31 2026). Store it in Settings > CI/CD > Variables as **Masked + Protected**, never as a file in the repo. **(blocked: needs Maintainer)**
  - If project access tokens aren't available on our tier, skip this. The monitor job then **fails the scheduled pipeline** with the drift report, instead of opening an issue.
- [ ] **Pipeline schedule** _(Developer can do this)_. Build > Pipeline schedules > New schedule:
  - Description: "Live site drift monitor"
  - Interval: every 30 minutes (`*/30 * * * *`)
  - Target branch: `main`
  - **No variables.** Every scheduled pipeline runs only the monitor job. This project blocks pipeline variables for Developers, which is why `EIG_JOB` was dropped.
  - The job checks https://showcase-0b6166.gitlab.io (`EIG_SITE_URL` in `.gitlab-ci.yml`).
  - To run it on demand, press ▶ (Play) on the schedule.
- [x] **First release** _(Developer can do this; done 2026-10-21, commit `1604be91`)_. On the latest `main` pipeline, press **Run** on the manual `release-pages` job. The deploy is human-only on purpose.

## Phase 4: Duo flow

- [ ] **Confirm the AI menu.** The left sidebar shows **AI > Flows / Agents / Triggers**.
- [x] **Create labels** _(done with the API on 2026-10-21; Developer can do this)_. Manage > Labels:
  - `integrity::block` (red)
  - `integrity::warn` (amber)
  - `integrity::pass` (green)
  - `integrity-incident`
  - `results-update`
- [ ] **Create the flow**: follow [`docs/duo-setup.md`](duo-setup.md), using `.gitlab/duo/flows/integrity-review.yml`: AI > Flows > New flow, visibility Private. **(blocked: needs Maintainer)**
- [ ] **Enable the flow** in this project. This creates its service account, which has the Developer role and **cannot merge** to protected `main`. **(blocked: needs Maintainer)**
- [ ] **Create triggers.** AI > Triggers > New flow trigger: **(blocked: needs Maintainer)**
  - Pipeline events: Passed, Failed
  - Mention
- [x] **Create the custom agent** "Integrity Advisor" from `.gitlab/duo/agents/integrity-advisor.md`. _(Created and enabled with GraphQL on 2026-10-22: item 1019155, consumer 12958692.)_
- [x] **Pipeline schedule** "integrity monitor" (ID 4504749, `*/30 * * * *`, `main`, no variables). Created with the API on 2026-10-21. The first run, pipeline #2973392233, was green. _(Developer can do this.)_
