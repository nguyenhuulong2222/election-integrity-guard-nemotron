# Recording and submission checklist (Long)

Internal deadline: **Mon Oct 26, 9:00 pm HST**. Hard deadline: Tue Oct 27, 3:00 am HST (13:00 UTC).

Project: https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43545862/showcase

## 0. One-time UI settings (before recording day)

The REST API refused these with 403, so they're UI-only. Set them once:

1. ✅ Done 2026-10-22. **Settings > Merge requests > Merge checks:**
   - **Pipelines must succeed:** ON
   - **All threads must be resolved:** ON

   Without "Pipelines must succeed", !1 to !3 are mergeable today, and shot 5 depends on it.
2. ✅ Done 2026-10-22. **Settings > Merge requests > Merge request approvals > Approval settings:**
   - **Prevent approval by author:** OFF
   - **Remove all approvals when commits are added:** ON

   Then **Save changes**. The "Election official" rule (1 approval, you as approver) already exists. Without this, Approve is missing on !4, and you'd use the backup line.
3. ✅ Done 2026-10-22. **AI > Flows > Election Integrity Guard > Edit:** paste `.gitlab/duo/flows/integrity-review.yml` from the repo (the whole file) and save. This adds the backtick formatting rule for future reviews. It doesn't change the existing notes.
4. Optional, to test the agent: open MR !3, open **GitLab Duo Chat** (right sidebar), choose the **Integrity Advisor** agent and ask "Why was !3 blocked?". It's read-only and posts nothing on the MR.

## 1. Pre-flight (5 minutes before recording)

- [ ] **!1, !2 and !3 can't be merged:** the merge widget says the pipeline must succeed.
- [ ] **!4:** pipeline green, `integrity::pass`, no unresolved threads, Approve visible (or plan the backup line), Merge available after approval.
- [ ] !1, !2 and !4 have one "EIG Duo review · pipeline" note each. !3 has two; record the newer one (09:07). **Do not re-run their pipelines.**
- [ ] The live site shows **Update 3** at https://showcase-0b6166.gitlab.io/.
- [ ] Build > Pipeline schedules: the latest "integrity monitor" pipeline is green.
- [ ] Open the 9 tabs listed in `docs/video-script.md`.
- [ ] Do Not Disturb on, notifications off, bookmarks bar hidden, autofill closed.
- [ ] Microphone level checked. No music playing anywhere.

## 2. Record

- Follow `docs/video-script.md` shot by shot. Target 2:40 and never over 2:45.
- One take per shot is fine. Cut together in any editor, with no added music.
- Shots 7 to 9 change real state (approve, merge, release). If one fails, see "If X fails, do Y" below, and don't merge anything else.

## 3. YouTube upload

- **Visibility:** **Public**. The rules say "publicly visible on YouTube".
- **Audience:** not made for kids. No music, so no Content ID issues.
- **Title:**
  ```
  Election Integrity Guard: supervised GitLab Duo workflow for election websites
  ```
- **Description:**
  ```
  Election Integrity Guard reviews every merge request to an election website. A deterministic checker gates CI, a GitLab Duo Agent Platform custom flow explains each result in plain English and labels the MR, and a human approves, merges and releases.

  Fictional demo data: Kanaloa County, its candidates and results do not exist.
  GitLab Transcend Hackathon, Path A (Start Fresh), autonomy level: Supervised.

  Code (MIT): https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43545862/showcase
  Live demo: https://showcase-0b6166.gitlab.io
  ```
- Check after upload: the length shows under 3:00, and the video plays in a private or incognito window.

## 4. Devpost submit

1. Put the YouTube URL in `docs/devpost.md` and `docs/devpost-submit.md` (replace `https://youtu.be/REPLACE_ME` and the `FILL: YouTube URL` marker). Commit and push. You can also ask Claude to do it.
2. Open the Devpost submission form. Paste each field from `docs/devpost-submit.md`.
3. Upload the images: `docs/screenshots/cover.png` first, then the six listed in `docs/devpost.md`.
4. Select **Path A** and **Best Supervised Agent**, plus the special prize **Most Stages Covered**.
5. Submit. Then open the public project page logged out and check that the video, links and images show.

## If X fails, do Y

| If… | Then… |
|---|---|
| Approve isn't shown on !4 | Use the backup line in the script and merge directly. Fix "Prevent approval by author" afterwards for completeness. |
| Merge is disabled on !4 | Read the merge widget's reason. "Pipeline must succeed": the head pipeline is #2975542189 (green), so refresh the page. "Unresolved threads": resolve them (the flow posts plain notes, not threads). "Approval required": approve first. |
| `release-pages` has no Run button | Open the new `main` pipeline (not the MR one). The job is manual and only appears on `main`. |
| The release job fails | Show the failure honestly, re-run the job once, and narrate the retry. Don't edit the site by hand. |
| The flow posts another review after the merge | It shouldn't: the trigger only fires for MR pipelines. If it does, delete nothing. Note it and mention it to Claude afterwards. |
| The live site doesn't update after 2 minutes | Check the `release-pages` job log for the deploy, then hard-reload. Pages can lag. |
| The monitor pipeline is red | That means drift, so don't record shot 10 that way. Check its log; after the release it should pass on the next run. Press ▶ on the schedule to run it now. |
| The video runs over 2:45 | Trim shot 2, then shot 10. Never cut shots 3, 5 or 7. |
