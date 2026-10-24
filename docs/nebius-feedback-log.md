# Build log: Token Factory, Nemotron and Tavily friction

Real observations made while building the Nemotron Integrity Agent, recorded when they
happened. Source material for the feedback section of DEVPOST.md.

## 2026-10-24 (Milestone 1)

**Token Factory**

1. **`GET /v1/models?verbose=true` is excellent.** It returns per-token prices, context length,
   rate limits and region per model. Our cost log uses those prices directly instead of
   copying them from a web page. The plain `/v1/models` call does not include them, and the
   `verbose` flag was not obvious; we found it by trying.
2. **How to turn reasoning off is not discoverable.** Every Nemotron model lists
   `supported_features: ["tools", "reasoning"]`, but nothing says how to control it.
   `extra_body={"chat_template_kwargs": {"enable_thinking": false}}` works on all four text
   models (completion dropped from 252 to 8 tokens on a trivial prompt with Lightning).
   `reasoning_effort="low"` is accepted but behaves differently per model: Lightning still
   produced about 450 characters of reasoning, Ultra produced none.
3. **Reasoning tokens count against `max_tokens`.** Lightning spent 227 reasoning tokens to
   answer "17 × 3" as JSON. A tight cap silently becomes `finish_reason: "length"` with an
   empty or partial answer. Our client treats `length` as an error and sizes caps per role.
4. **The reasoning fields are inconsistent across models.** Lightning and Super return both
   `message.reasoning` and `message.reasoning_content`, while Nano returns only `reasoning`.
   Nano also omits `usage.completion_tokens_details`, so reasoning tokens show as "not
   reported" for Nano in our logs.
5. **Structured output works but is not advertised.** `response_format` with `json_object`
   and with strict `json_schema` worked on Lightning, Nano and Super. Neither appears in
   `supported_features` or `supported_sampling_parameters`. Without `response_format`,
   Super's JSON reply starts with `"\n\n"`.

**Nemotron (model behaviour)**

6. **Super 120B needed one domain rule for a subtle case.** Fixture T03 adds 1,400
   "provisional ballots" that all land on one side of one measure, with a real-looking
   ticket. With the first prompt, Super called it legitimate at 0.92 confidence: it checked
   the ticket's words, not physical plausibility. After one general rule ("a ballot carries
   every contest, so new ballots should move several contests"), it answered tampering at
   0.88 and still judged the documented correction T04 legitimate. The eval reports the
   prompt version, and later held-out cases are written after the prompt is frozen.
7. **Cost is small.** A tamper triage with Super costs about $0.001–0.002. The Ultra incident
   report costs about $0.003. The first 12 live calls cost $0.021 in total.

## 2026-10-24 (Milestone 2)

**Tavily**

8. **The default Extract output dropped content.** For our voter-information page, Extract with
   the default markdown format returned 903 characters: headings survived, but the list of
   drop-box addresses, the link text and most of the dates table were missing. Adding
   `"format": "text"` (or `extract_depth: "advanced"`) returned the full 1.3–1.6 KB, including
   lists and tables. For fact-checking use cases, the default silently loses the facts.
9. **Bearer auth and latency are good.** `Authorization: Bearer` works for `/search` and
   `/extract`. Search took 0.4–1.9 s and Extract took 0.4–0.9 s. The responses do not include
   credit usage unless asked, so our log records calls and result counts, not credits.
10. **The search results for a fictional jurisdiction are honest.** Queries about "Kanaloa County"
   return real election pages from New Jersey, Mississippi and other states (relevance
   scores 0.07–0.45). That is correct behavior, and it is why the hunter needs a "never
   accuse a page that does not mention the county" guard in code.

**Nemotron**

11. **Lightning (thinking off) skipped one field in 3 of 4 languages until each field was
   described.** With bare field names, `mail_ballots_sent` came back empty for vi/es/tl even
   though the row was on the page. One line of description per field fixed it: the
   consistent scenario then gave 0 false mismatches and the drift scenario caught 3 of 3.
12. **Lightning sometimes returned a partial list.** One search-triage reply covered fewer than
   the 16 input items (47 completion tokens, with `finish_reason: stop` and valid JSON for the
   schema). The same input then returned all 16. The schema cannot express "one entry per
   input id", so the client now runs a coverage check and retries once.
13. **Super's corrected Tagalog sentence was not fluent.** In one explanation of a missing
   field, Super's suggested Tagalog fix used non-standard words. The Vietnamese and Spanish
   fixes read naturally. The UI labels every suggested fix as "draft for a human translator".
