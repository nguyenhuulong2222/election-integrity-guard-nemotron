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
