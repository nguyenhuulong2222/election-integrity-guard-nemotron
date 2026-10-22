# Video script: Election Integrity Guard (target 2:40, hard limit 2:45)

> DRAFT. Nothing is recorded yet. `[CAPTURE: ...]` marks a screen to record; `[SCREENSHOT: ...]` marks a still to grab for the README and Devpost.
> **Audio:** voice only, no music (the rules ban copyrighted music; silence is safest). **Language:** English. **Resolution:** 1920×1080, browser zoom 125%, light mode.
> Narration is about 320 words, roughly 2:10 at 150 words per minute. That leaves about 30 seconds for on-screen pauses, clicks and page loads.

Two versions share most shots. **Record version A.** The flow went live on 2026-10-21 with the Developer+ role, and the Pipeline events trigger fires automatically. Shots marked **A** are for that version. Shots marked **B** are for Plan B, where the flow runs from the GitLab for VS Code flow builder. Record only the version that matches reality, and never show something that didn't happen.

---

## Before you record

- [ ] The Duo review comment exists on !1, !2 and !3 (A: re-run each MR pipeline after the trigger is enabled; B: run the flow from VS Code once per MR).
- [ ] The labels `integrity::block` (!1–!3) and `integrity::pass` (!4) are visible.
- [ ] An incident issue was opened by the flow for at least !2 or !3.
- [ ] !4 is still open and unmerged, with a green pipeline and no review yet (A), or with the PASS review (B).
- [ ] Tabs open, in order:
  1. live site (results page)
  2. README diagram
  3. MR !2
  4. MR !3
  5. MR !1
  6. MR !4
  7. Build > Pipelines
  8. Build > Pipeline schedules
- [ ] Notifications off, bookmarks bar hidden, a clean browser profile.

---

## Shot list

| # | Time | Screen | Narration |
|---|---|---|---|
| 1 | 0:00–0:10 | `[CAPTURE: live site results page, slow scroll; the yellow "Fictional demo data" band is visible]` | "This is an election results page. The county is fictional, but the risk is real: whatever merges here is what voters see on election night." |
| 2 | 0:10–0:24 | `[CAPTURE: three diffs in a split view: !1 votes line, !2 domain with one hyphen, !3 script tag and CSP]` | "One merge can publish impossible totals, swap the polling-place link for a lookalike domain, or slip in a third-party script. In a three-line diff at 11 p.m., a reviewer won't see one hyphen." |
| 3 | 0:24–0:42 | `[CAPTURE: README Mermaid diagram, zoomed; highlight each box as it is named]` `[SCREENSHOT: architecture diagram]` | "Election Integrity Guard is a supervised GitLab Duo workflow. A deterministic checker runs in CI and blocks bad changes. Then a GitLab Duo custom flow reads its report and the diff, and explains the result to an election official. A human releases. The agent can't merge, approve or deploy." |
| 4A | 0:42–1:04 | `[CAPTURE: MR !2: failed pipeline badge → Code Quality widget "1 blocker" → scroll to the Duo review comment → label integrity::block]` `[SCREENSHOT: Duo review on !2]` | "Here someone 'moved the polling-place lookup to a new vendor.' The pipeline fails. Duo's review explains it in plain English: kanaloa-hyphen-county imitates the official domain, so voters would leave the real site without noticing. It labels the MR and points to the fix." |
| 4B | 0:42–1:04 | `[CAPTURE: VS Code, GitLab flow builder with integrity-review.yml open → Run with goal "Input: review\nContext: {MergeRequest IID: 2}" → tool calls stream → switch to MR !2 showing the new comment + label]` `[SCREENSHOT: Duo review on !2]` | "Here someone 'moved the polling-place lookup to a new vendor.' The pipeline fails. I run our Duo flow from the GitLab flow builder against this MR. It reads the checker report and the diff, and explains in plain English that kanaloa-hyphen-county imitates the official domain. Then it labels the MR." |
| 5 | 1:04–1:26 | `[CAPTURE: MR !3 diff (script tag, CSP line) → Code Quality "5 blockers" → Duo review section on the CSP → click the "Opened incident issue" link → the issue page]` `[SCREENSHOT: Code Quality widget on !3]` | "An 'analytics tag': a third-party script, an inline script, and a Content Security Policy loosened to allow both. The checker compares the CSP with main, so even a single added host is caught. For a BLOCK, the flow opens an incident issue that a human must triage." |
| 6 | 1:26–1:38 | `[CAPTURE: MR !1 Duo review "Votes do not add up: 30,902 vs 29,402"]` | "And a 'recount' that adds 1,500 votes to one candidate but not to the contest total. Blocked, with the exact numbers." |
| 7A | 1:38–2:04 | `[CAPTURE: MR !4: green pipeline → Duo review "PASS", label integrity::pass → click Approve → Merge → Build > Pipelines → main pipeline → press Run on release-pages]` | "A legitimate update passes, and Duo says so. But passing isn't publishing. I review it as the election official, then approve and merge. The release job waits for a person to press Run. The AI never deploys." |
| 7B | 1:38–2:04 | Same as 7A. The PASS review comes from the VS Code run in step 4B's setup. | Same as 7A. |
| 8 | 2:04–2:20 | `[CAPTURE: live site shows "Update 4" → Build > Pipeline schedules "integrity monitor" → latest monitor job log "No drift, 7 files compared"]` | "Update 4 is live. Every thirty minutes, a scheduled pipeline compares every live file's hash with the reviewed commit. If someone edits the site after release, the pipeline goes red." |
| 9 | 2:20–2:34 | `[CAPTURE: README "DevSecOps stages covered" table, slow scroll]` `[SCREENSHOT: stage table]` | "Plan, create, verify, secure, package, release, configure, monitor and govern, all in GitLab, with 64 tests behind the rules." |
| 10 | 2:34–2:42 | `[CAPTURE: back to the results page; the repo URL overlaid as text]` | "Code enforces. Duo explains. People decide. That's Election Integrity Guard." |

**Total: 2:42.** If you run long, trim shot 6 first, down to 6 seconds, then shot 9.

---

## Honesty notes

- Say "fictional" at least once on screen (the banner) and once in narration (shot 1).
- In version B, don't show or describe a trigger firing automatically. Say "I run our Duo flow".
- If "Approve" isn't available on !4 (the approval rule is Maintainer-only), cut "approve and" from shot 7 and show Merge directly.
- Don't show tokens, the glab login, or personal emails. Check the browser autofill before recording.

## Upload checklist

- [ ] Length < 3:00 (target ≤ 2:45). No music.
- [ ] YouTube visibility: Public or Unlisted, as the rules allow. Title: "Election Integrity Guard: supervised GitLab Duo workflow for election websites".
- [ ] Description: the repo link, the live demo link, "Fictional demo data", and "Path A, Supervised".
- [ ] Paste the URL into `docs/devpost.md` and the Devpost form.
