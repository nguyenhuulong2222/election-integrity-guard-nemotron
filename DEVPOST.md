# Devpost drafts: Nemotron Integrity Agent

Paste-ready text for the Nebius × NVIDIA Global AI Hackathon submission ("Best Apps and Agents").
Replace `VIDEO_URL_PLACEHOLDER` with the YouTube link.

**Links**
- Demo: https://eig-nemotron.onrender.com (live through the end of judging, Dec 15, 2026; live runs are rate-limited, Replay always works)
- Code (MIT): https://github.com/nguyenhuulong2222/election-integrity-guard-nemotron
- Video: VIDEO_URL_PLACEHOLDER

---

## Project name and tagline

**Nemotron Integrity Agent:** deterministic checks detect every change to an election website; NVIDIA Nemotron on Nebius Token Factory decides what each change means and who must look at it; a person makes the final call.

## Inspiration

After an election, the most trusted page in a county is its results page, and it runs on an ordinary website. Even certified numbers can be changed. A careful attacker keeps every total consistent, so arithmetic checks pass. Translated voter pages drift: one wrong date in the Tagalog page can send voters to the polls a day late. And lookalike sites announce that "Election Day has moved". We wanted an agent that helps a small elections office catch all three, without ever letting a model make the final decision.

## What it does

Three features, each built the same way: deterministic code detects, Nemotron reasons, a person decides.

1. **Results Seal + tamper triage.**
   - The SHA-256 of the certified results is the seal. Any difference on the live site is detected, with no AI involved.
   - Nemotron Super 120B then judges whether the change is legitimate, tampering or uncertain, with evidence. It does this twice, independently.
   - A code gate turns that into one of three outcomes: **rollback recommended** (restore the certified copy and notify the duty official), **escalate** to a person, or **official sign-off**.
   - Nothing is ever silently accepted. A Nemotron error changes how urgently a human sees the change, never whether it is detected.
   - After a rollback decision, Nemotron Ultra 550B writes the incident report.
2. **Multilingual consistency.**
   - Nemotron Lightning reads the English, Vietnamese, Spanish and Tagalog voter pages in parallel and extracts the dates, times, sites and phone number, each with a verbatim quote.
   - Code verifies each quote is really on the page and compares the facts with the certified calendar.
   - Super explains each mismatch, its impact on voters, and drafts a fix in that language for a human translator.
3. **Misinformation hunter.**
   - Tavily Search and Tavily Extract look for pages about the county election at runtime.
   - Lightning triages the results; code checks for contradictions and lookalike domains.
   - Super writes a report that cites each URL.
   - A code guard ensures a page that never mentions the county is never accused. The demo's positive findings come from two clearly labeled, noindexed decoy pages.

Every pipeline step shows its model, tokens, latency and cost in the UI.

## How we built it

- **Nebius Token Factory with the OpenAI SDK.**
  - Every call names a role rather than a model: FAST (Lightning, reasoning off), REASONING (Super 120B, reasoning on) and REPORT (Ultra 550B).
  - Every call uses a strict JSON schema, validated again locally, with one retry; an invalid reply routes to a person.
  - Reasoning is toggled per role with `chat_template_kwargs.enable_thinking`.
  - Prices come from `GET /v1/models?verbose=true`, and each call logs its tokens, latency and cost.
- **The FAST model was picked by an eval, not by guessing.** On translation drift, Lightning got 14 of 14 scenarios exactly right and Nano 30B got 3 of 14, at the same price.
- **An eval with held-out sets.** Each held-out set was committed before it was run, and the triage prompt was frozen by hash. Everything ran twice, and every result, including the bad ones, is in the README.
- **Gate v2 (self-consistency):** two independent Super verdicts must agree before the gate recommends a rollback.
- **Deterministic risk signals for the human signer:** a service-account actor, an off-hours change, a ticket that doesn't match the size of the diff, a one-sided vote removal, a drop in registered voters. They are informational only, never used by the gate.
- **Tavily over REST** at runtime, and a stdlib Python web server deployed on Render with server-side secrets, a strict CSP, and rate limits.
- **Reuse.** The deterministic rules (results arithmetic and lookalike-domain detection) come from our earlier GitLab project and are imported unchanged.

## Challenges we ran into

- **Disguised tampering.** On our second held-out set, Super sent 5 of 6 disguised-tampering runs to human sign-off as "legitimate" under gate v1, and 3 of 6 under v2. A service account cutting registered voters at 02:40 through an API token was judged legitimate in all 6 calls. Plausible paperwork persuades the model. This is why "legitimate" is never automatic approval, and why the signer sees risk signals.
- **Temperature 0 is not deterministic.** The same request flipped verdicts between runs, so we report every run and added the two-vote gate. Even so, both votes were sometimes wrong together.
- **A translation that was ambiguous, not wrong.** A Vietnamese label meaning "vote by mail" did not state that the county *mails* ballots on that date, and the extractor rightly reported the fact as missing. A native-speaker fix to the label, not prompt tuning, solved it.
- **Tavily Extract's default markdown output dropped list and table content** on our pages; `format: "text"` kept it.

## Accomplishments that we're proud of

- **Detection is 100% deterministic**, and every outcome routes to a person. The AI adds triage and explanation without becoming a single point of failure.
- **We measured honestly:** held-out sets committed before running, a frozen prompt, two repeats, and the failure cases published.
- **A demo that is safe to share:** recorded runs replay at no cost, live runs are rate-limited, keys never reach the browser, and decoys are labeled and noindexed.
- **Cheap to run:** a full tamper triage with two Super votes and an Ultra report costs under a cent.

## What we learned

- Use the smallest model that the eval supports for each role. Lightning beat the reasoning-heavy alternatives for extraction; Super earned its cost on judgment calls.
- Self-consistency helps less than hoped when errors are correlated, so the human checkpoint has to be designed in, not bolted on.
- Writing held-out cases *before* running them changes what you are willing to claim.

## What's next

- A visual defacement check with Nemotron 3.5 Super VL (comparing a live screenshot with the certified screenshot).
- Signing the certified file (not just hashing it), and an append-only log of official sign-offs.
- Larger fixture sets written by election administrators, and a held-out set for the risk signals.

## Built with

NVIDIA Nemotron (3.5 Lightning, 3 Super 120B, 3 Ultra 550B) · Nebius Token Factory · OpenAI Python SDK · Tavily Search and Extract API · Python 3.12 (standard library) · Render · GitHub

---

## What was significantly updated during the Submission Period

This is a **new project, created entirely within the Submission Period** (which opened August 26, 2026, 9:00 AM PT). The git history is the evidence: the first commit is dated October 20, 2026. The deterministic base (a fictional county site, a Python integrity checker and GitLab CI) was built October 20–23, 2026, with no Nebius, Nemotron or Tavily code. The Nemotron and Tavily layer was added from October 24, 2026 on the `nebius-nemotron` branch:

- the `nemotron_agent/` package:
  - the Token Factory client with role routing, strict JSON schemas, bounded retries and a per-call cost log;
  - Results Seal tamper triage with gates v1 and v2, plus the Ultra incident report;
  - the 4-language consistency check;
  - the Tavily misinformation hunter;
  - deterministic risk signals;
- an eval harness with 29 fixtures (held-out sets committed before they were run) and a results file for every run;
- the web demo (API, UI with live per-step progress, recorded runs, rate limits, labeled decoy pages) and its Render deployment;
- documentation and a feedback log written during the build.

---

## Feedback: Token Factory, Nemotron, Tavily

Everything here was observed while building; the dated log is in `docs/nebius-feedback-log.md`.

### Nebius Token Factory

1. **`GET /v1/models?verbose=true` is a hidden gem. Document it and make it the default.** It returns per-token prices, context length, rate limits and region for every model, which let us compute cost per call from the API itself instead of copying a price page. The plain `/v1/models` call returns none of this, and we found `verbose` by trying.
2. **Document how to control reasoning.** Every Nemotron model advertises `supported_features: ["reasoning"]`, but nothing says how to turn it off.
   - `extra_body={"chat_template_kwargs": {"enable_thinking": false}}` works on all four text models: on the same trivial JSON prompt, Lightning used 8 completion tokens with it, against 152 with `reasoning_effort="low"`.
   - `reasoning_effort="low"` is accepted but behaves differently per model: Lightning still produced about 450 characters of reasoning, Ultra none.
3. **Reasoning tokens count against `max_tokens`, so a tight cap silently returns nothing.**
   - Lightning spent 227 reasoning tokens to answer "17 × 3" as JSON.
   - With reasoning on, Lightning hit our 6,000-token cap in 7 of 30 tamper-triage runs, finishing with `finish_reason: "length"` and no answer.
   - A separate reasoning budget (or a warning when reasoning used most of the cap) would prevent this.
4. **Make the response shape consistent across models.** Lightning and Super return both `message.reasoning` and `message.reasoning_content`; Nano returns only `reasoning` and omits `usage.completion_tokens_details`, so reasoning-token accounting breaks for one model family.
5. **Advertise structured output.** Strict `json_schema` worked on every Nemotron model we tried, but neither `response_format` nor JSON mode appears in `supported_features` or `supported_sampling_parameters`. We only found it by testing.
6. **Offer a determinism option for audits.** Identical requests at temperature 0 returned different safety-relevant verdicts. For example, a legitimate recount was judged "legitimate 0.85" in one run and "tampering 0.90" in another. A seed parameter, or documentation of what determinism to expect, matters for anyone using LLMs in a decision workflow.

### NVIDIA Nemotron

7. **Super 120B was the best judge, and fast**: a median of 6–10 s per triage with reasoning on, $0.001–0.002 per call. That beat Lightning and Nano with reasoning on, both in our accuracy table and in latency.
8. **Lightning with reasoning off is excellent at extraction**: 14 of 14 multilingual drift scenarios exactly right, with every value backed by a verbatim quote from the page, for under $0.001 per 4-language run. Nano 30B over-reported mismatches (3 of 14).
9. **Plausible paperwork persuades the model.** Disguised tampering with an approved-looking ticket was Super's main failure (H12: judged legitimate in all 6 calls). A system prompt rule helped one case (T03); a second rule would have been overfitting. Guidance on adversarial-evidence prompting for Nemotron would help.
10. **Lightning occasionally returned a partial list that still passed the schema** (one triage covered fewer items than the 16 it was given, ending `finish_reason: stop`). We added a coverage check and a retry. The schema cannot say "one entry per input id".

### Tavily

11. **Extract's default markdown output silently dropped content we needed.** For our voter-information page it returned 903 characters: headings survived, but the list of drop-box addresses and most of a dates table were missing. `format: "text"` (or `extract_depth: "advanced"`) returned 1.3–1.6 KB, including everything. For fact-checking, a default that loses list items is risky; consider keeping list and table text in markdown mode.
12. **Fast and simple.** Bearer auth worked on `/search` and `/extract`, with 0.4–1.9 s latency. Credit usage is not in responses by default, so per-call cost logging needs an extra flag.
13. **Honest results for a fictional jurisdiction.** Searching a county that doesn't exist returns real election pages from other states (scores 0.07–0.45), which is correct, but it means any "misinformation hunter" must guard against accusing real, unrelated sites. We enforce that in code.

---

## Video script (target 2:40, hard limit 3:00)

Record the deployed demo at https://eig-nemotron.onrender.com, logged out, at a 1920×1080 desktop size. Open the site once before recording, because Render's free tier needs about 30–60 s to wake up. The narration is about 350 words. Use no music. If the voice is AI-generated, say so in the YouTube description.

| Time | On screen | Narration |
|---|---|---|
| 0:00–0:15 | Demo home page; "Fictional demo data" banner; slowly hover over the three model chips | "After an election, the results page is the most trusted page in a county, and it runs on an ordinary website. This is the Nemotron Integrity Agent, guarding a fictional county's election site with NVIDIA Nemotron on Nebius Token Factory." |
| 0:15–0:35 | Click **Run live** on "Votes moved, totals kept"; the step list fills in: Seal ✓, Super ×2 running | "Rule one: detection is deterministic. The Results Seal is a SHA-256 hash of the certified results. Here someone moved sixteen hundred votes between two candidates and kept every total consistent, so arithmetic checks pass. The hash catches it anyway, with no AI involved." |
| 0:35–1:05 | Both verdict boxes appear (tampering 0.9x); scroll to the evidence list, the diff table and the risk signals | "Now Nemotron Super reasons about what the change means. It is asked twice, independently. Both verdicts say tampering: a service account, a direct upload, no ticket. Only because both agree does the gate, which is plain code, recommend a rollback and notify the duty official, who confirms or reverses it. The official also sees deterministic risk signals: service account, three in the morning, a diff bigger than any ticket explains." |
| 1:05–1:15 | Scroll to the incident report (Ultra) and the calls table with tokens and cost | "Nemotron Ultra drafts the incident report. Every call shows its model, tokens, latency and cost. This whole run cost under a cent." |
| 1:15–1:35 | Click **Replay** on "Documented correction", then "Ticket can't be verified" | "Not every change is an attack. A canvass-board correction goes to an official for sign-off, never automatic approval. A change whose ticket can't be verified goes to a person. Nothing is ever silently accepted." |
| 1:35–2:00 | Click **Replay** on "Translations drift"; show the mismatch table (tl Nov 4, es 6 pm, vi lookalike domain) | "Voters read in many languages. Nemotron Lightning extracts the facts from English, Vietnamese, Spanish and Tagalog pages in parallel, each backed by a verbatim quote. Code compares them with the certified calendar. Super explains the impact: a Tagalog reader would arrive a day late; a Vietnamese reader would visit a lookalike site. It drafts fixes for a human translator." |
| 2:00–2:25 | Click **Run live** on "Hunt misinformation"; show the Tavily step, the results table (mostly "unrelated"), the two decoy findings with URLs | "Misinformation lives elsewhere. Tavily searches the live web and extracts our watchlist. Lightning triages every result, and code makes sure a page that never mentions the county is never accused. Super reports two labeled demo decoys, citing their URLs: a fake date change, and a lookalike registration site." |
| 2:25–2:45 | Scroll the README eval section on GitHub: the gate v1/v2 table | "We measured it honestly, with held-out cases committed before they were run. Lightning won extraction fourteen out of fourteen. Super's weak spot is disguised tampering with approved-looking paperwork. That is exactly why the hash detects, and a person decides. Nemotron Integrity Agent." |

---

## Short description (for the Devpost card, at most 200 characters)

Deterministic hashes detect every change to an election site; NVIDIA Nemotron on Nebius Token Factory triages, explains and drafts reports; Tavily hunts misinformation; a person decides.
