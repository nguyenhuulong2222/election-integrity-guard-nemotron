# Video script: Election Integrity Guard (version A, final; target 2:40, hard limit 2:45)

> `[CAPTURE: ...]` marks a screen to record.
> **Audio:** voice only, no music. **Language:** English. **Resolution:** 1920×1080, browser zoom 125%, logged in as yourself.
> Narration is about 330 words, roughly 2:12 at 150 words per minute, which leaves about 30 seconds for clicks and page loads.

Everything shown really happened: the Election Integrity Guard flow ran from its Pipeline events trigger on 2026-10-22 and reviewed !1 to !4. Pre-flight checks are in [`long-checklist.md`](long-checklist.md).

---

## Tabs to open, in this order

1. Live site, results page: https://showcase-0b6166.gitlab.io/results.html
2. MR !3, Overview tab, scrolled to the **newest** Election Integrity Guard review (09:07, after the "@… review" mention; it lists all five blockers)
3. Pipeline #2975541950, **Code Quality** tab (!3's five blockers)
4. MR !1, Overview tab (merge widget visible)
5. MR !4, Overview tab
6. Build > Pipelines (stays open, to refresh after the merge)
7. Live site home: https://showcase-0b6166.gitlab.io/
8. Build > Pipeline schedules
9. README on the project page, scrolled to "DevSecOps stages covered"

---

## Shot list (exact click order)

| # | Time | Screen and clicks | Narration |
|---|---|---|---|
| 1 | 0:00–0:12 | **Tab 1** live results page. Slow scroll; the yellow "Fictional demo data" band stays visible. | "This is a county election results page. The county is fictional, but the risk is real: whatever merges here is what voters see on election night." |
| 2 | 0:12–0:24 | Stay on tab 1, pointing at the Mayor totals. | "One merge can publish impossible totals, send voters to a lookalike polling-place site, or slip in a third-party script. In a three-line diff at 11 p.m., nobody sees one hyphen." |
| 3 | 0:24–0:50 | **Tab 2** MR !3. Show the `integrity::block` label, then the review note from **Election Integrity Guard**: "BLOCK", "What this means", the ASSET-001 finding. | "Election Integrity Guard is a supervised GitLab Duo workflow. A deterministic checker runs in CI. When the pipeline finishes, our custom Duo flow starts automatically, reads the checker report and the diff, and writes this review for an election official. Here, an 'analytics tag' loads code from an outside company onto the results page." |
| 4 | 0:50–1:04 | **Tab 3** Code Quality tab: five Blocker rows (ASSET-001, ASSET-002, CSP-002/003/004). | "The checker found five blockers, including a Content Security Policy loosened to let that script run. The flow labelled the MR and opened an incident issue for a human to triage." |
| 5 | 1:04–1:20 | **Tab 4** MR !1: the merge widget shows the merge is blocked because the pipeline failed. Then hover the `integrity::block` label. | "A 'recount' that adds 1,500 votes to one candidate but not to the total. The pipeline failed, so GitLab won't let anyone merge it. The same holds for the lookalike link and the script. The agent explains; the gate is code." |
| 6 | 1:20–1:36 | **Tab 5** MR !4: green pipeline, `integrity::pass` label, the review "PASS" with its advisory notes. | "Results update four passes. Duo says so, adds the totals it checked, and reminds the approver that a person still decides." |
| 7 | 1:36–1:56 | Still on !4: click **Approve**, then **Merge**. | "I review it as the election official, approve it, and merge. The agent has no merge, approve or deploy tool, and its service account can't push to main." |
| 8 | 1:56–2:12 | **Tab 6** Build > Pipelines → refresh → open the new `main` pipeline → press **Run** (▶) on `release-pages` → wait for the job to start. | "Merging isn't publishing. The release job waits for a human to press Run." |
| 9 | 2:12–2:22 | **Tab 7** live site home, reload: "Update 4, Tue, Nov 3, 11:45 PM HST". | "Update four is live." |
| 10 | 2:22–2:32 | **Tab 8** Pipeline schedules "integrity monitor" → latest pipeline (green) → `monitor` job log "No drift". | "Every thirty minutes, a scheduled pipeline compares every live file's hash with the reviewed commit. Tampering after release turns it red." |
| 11 | 2:32–2:42 | **Tab 9** README "DevSecOps stages covered" table, slow scroll. | "Plan, create, verify, secure, package, release, configure, monitor and govern, all in GitLab. Code enforces. Duo explains. People decide." |

**Total: 2:42.** If you run long, cut shot 2 to 8 seconds, then shorten shot 10.

### Backup lines

- **Approve is missing or disabled on !4** (your account can't approve its own MR): skip the approve click. Say: "In production a separate election official approves here. In this one-person demo, I merge as that official." Then click **Merge**.
- **Merge is disabled on !4:** say "GitLab is holding the merge until its checks pass," then show the reason in the merge widget. Stop the shot and fix it off camera (see `long-checklist.md`).
- **`release-pages` takes more than 20 seconds:** cut to the live site after the job turns green. Say "a minute later…".
- **The live site still shows Update 3:** hard-reload (Cmd+Shift+R). Pages can take up to a minute.

## Honesty notes

- Say "fictional" in shot 1. The banner is visible in shots 1 and 9.
- Don't re-run pipelines on !1 to !3 before recording. Each run posts another review and opens another incident issue.
- !3 has two reviews. The first (08:38) stops rendering at "ASSET-002: Inline", because of a bare `<script>` tag. The second (09:07, after the mention) uses the fixed prompt and renders fully. Show only the second.
- Don't show tokens, terminal sessions or browser autofill.
