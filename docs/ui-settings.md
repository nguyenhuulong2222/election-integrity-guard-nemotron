# GitLab UI settings checklist

Project: `gitlab-ai-hackathon/transcend-october-2026/43545862/showcase` (ID `87857590`)

Some protections can only be set in the GitLab UI. Each item says which phase needs it.

> **Role blocker (2026-10-21).** The project owner's account currently has the **Developer** role (access level 30). Items marked **(blocked: needs Maintainer)** can't be changed until the organizers grant Maintainer. That was requested in issue #1, note 4060904922.

## Phase 1: now

- [x] **Visibility: Public.** Settings > General > Visibility, project features, permissions > Project visibility = **Public**. _(Already Public as of 2026-10-21.)_
- [ ] **Protected branch `main` (temporary settings).** Settings > Repository > Branch rules > `main`: **(blocked: needs Maintainer)**
  - Allowed to merge: **Maintainers**
  - Allowed to push and merge: **Maintainers** _(temporary, so Phases 2–4 can push directly)_
  - Allowed to force push: **off**
  - Code owner approval: **off for now.** With it on, GitLab *denies direct pushes to the protected branch when a CODEOWNERS rule matches* ([docs](https://docs.gitlab.com/user/project/repository/branches/protected/#require-code-owner-approval)), and Phases 2–4 push directly to code-owned paths. It is switched on before Phase 5.
- [ ] **Merge request approvals.** Settings > Merge requests > Merge request approvals: **(blocked: needs Maintainer)**
  - Approval rule "Election official": **1** approval required, eligible approvers = Maintainers (you)
  - Approval settings:
    - **Prevent approval by author: OFF** (demo only, see below)
    - Prevent approvals by users who add commits: OFF (demo only)
    - Remove all approvals when commits are added: **ON**
- [ ] **Merge checks.** Settings > Merge requests: **All threads must be resolved: ON**. _("Pipelines must succeed" waits until Phase 3.)_ **(blocked: needs Maintainer)**
- [x] **Pages.** Already turned on (API `pages_access_level: enabled`). The first deploy happens in Phase 3.

## After Phase 3 (once CI exists)

- [ ] **Merge checks.** Settings > Merge requests: **Pipelines must succeed: ON**. **(blocked: needs Maintainer)**

## Before Phase 5 (demo MRs)

- [ ] **Protected branch `main` (final settings).** Settings > Repository > Branch rules > `main`: **(blocked: needs Maintainer)**
  - Allowed to push and merge: **No one**, so every demo change goes through an MR
  - **Code owner approval: ON**

> **Why "Prevent approval by author" is off.** This is a one-person hackathon project, so the author is also the only approver. In production, a **separate election official** is the required approver, this setting stays **ON**, and the Duo service account is never an eligible approver.

## Phase 3: CI and release

- [ ] **Protected environment `production`.** Settings > CI/CD > Protected environments: allowed to deploy = Maintainers, **required approvals = 1**. _(Premium or Ultimate. Same solo-author caveat as above.)_ **(blocked: needs Maintainer)**
- [ ] **CI/CD variable `EIG_BOT_TOKEN`.** Create a project access token (Settings > Access tokens: role Reporter, scope `api`, expiry ≤ Oct 31 2026). Store it in Settings > CI/CD > Variables as **Masked + Protected**, never as a file in the repo. **(blocked: needs Maintainer)**
  - If project access tokens aren't available on our tier, skip this. The monitor job then **fails the scheduled pipeline** with the drift report, instead of opening an issue.
- [ ] **Pipeline schedule.** Build > Pipeline schedules > New: target `main`, every 30 minutes, variable `EIG_JOB=monitor`.

## Phase 4: Duo flow

- [ ] **Confirm the AI menu.** The left sidebar shows **AI > Flows / Agents / Triggers**.
- [ ] **Create labels.** Manage > Labels:
  - `integrity::block` (red)
  - `integrity::warn` (amber)
  - `integrity::pass` (green)
  - `integrity-incident`
  - `results-update`
- [ ] **Create the flow** from `.gitlab/duo/flows/integrity-review.yml`: AI > Flows > New flow, visibility Private. **(blocked: needs Maintainer)**
- [ ] **Enable the flow** in this project. This creates its service account, which has the Developer role and **cannot merge** to protected `main`. **(blocked: needs Maintainer)**
- [ ] **Create triggers.** AI > Triggers > New flow trigger: **(blocked: needs Maintainer)**
  - Pipeline events: Passed, Failed
  - Mention
- [ ] **Create the custom agent** "Integrity Advisor" (AI > Agents > New agent) from `.gitlab/duo/agents/integrity-advisor.md`. **(blocked: needs Maintainer)**
