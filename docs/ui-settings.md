# GitLab UI settings checklist

Project: `gitlab-ai-hackathon/transcend-october-2026/43545862/showcase` (ID `87857590`)

Some protections can only be set in the GitLab UI. Each item says which phase needs it.

## Phase 1: now

- [ ] **Visibility: Public.** Settings > General > Visibility, project features, permissions > Project visibility = **Public**. _(Already Public as of 2026-10-21.)_
- [ ] **Push the Phase 1 commits to `main` first**, then protect it.
- [ ] **Protected branch `main`.** Settings > Repository > Protected branches:
  - Allowed to merge: **Maintainers**
  - Allowed to push and merge: **No one** (every change goes through an MR, which also builds pipeline history)
  - Allowed to force push: **off**
  - **Code owner approval: on**
- [ ] **Merge request approvals.** Settings > Merge requests > Merge request approvals:
  - Approval rule "Election official": **1** approval required, eligible approvers = Maintainers (you)
  - Approval settings:
    - **Prevent approval by author: OFF** (demo only, see below)
    - Prevent approvals by users who add commits: OFF (demo only)
    - Remove all approvals when commits are added: **ON**
- [ ] **Merge checks.** Settings > Merge requests:
  - **Pipelines must succeed: ON**
  - **All threads must be resolved: ON**
- [ ] **Pages.** Settings > General > Visibility, project features, permissions > **Pages: on, Everyone**. The first deploy happens in Phase 3.

> **Why "Prevent approval by author" is off.** This is a one-person hackathon project, so the author is also the only approver. In production, a **separate election official** is the required approver, this setting stays **ON**, and the Duo service account is never an eligible approver.

## Phase 3: CI and release

- [ ] **Protected environment `production`.** Settings > CI/CD > Protected environments: allowed to deploy = Maintainers, **required approvals = 1**. _(Premium or Ultimate. Same solo-author caveat as above.)_
- [ ] **CI/CD variable `EIG_BOT_TOKEN`.** Create a project access token (Settings > Access tokens: role Reporter, scope `api`, expiry ≤ Oct 31 2026). Store it in Settings > CI/CD > Variables as **Masked + Protected**, never as a file in the repo.
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
- [ ] **Create the flow** from `.gitlab/duo/flows/integrity-review.yml`: AI > Flows > New flow, visibility Private.
- [ ] **Enable the flow** in this project. This creates its service account, which has the Developer role and **cannot merge** to protected `main`.
- [ ] **Create triggers.** AI > Triggers > New flow trigger:
  - Pipeline events: Passed, Failed
  - Mention
- [ ] **Create the custom agent** "Integrity Advisor" (AI > Agents > New agent) from `.gitlab/duo/agents/integrity-advisor.md`.
