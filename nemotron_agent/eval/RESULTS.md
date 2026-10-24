# Eval results (2026-10-24)

Repeats per case and model: 2. Temperature 0. Triage prompt SHA-256 `588f117b4a2d…`. Small fixture sets: read these as a sanity check, not a benchmark. Latency is wall-clock per run with 4 runs in flight at once (drift runs its 4 language extractions in parallel); a run that ends in an error still counts as wrong.

## Summary

Triage "verdict accuracy" scores the first verdict; "decision correct" scores what the gate did.

| Suite | Split | Model | Gate | Cases | Runs | Verdict accuracy | Decision correct | Median latency | Mean cost/run |
|---|---|---|---|---|---|---|---|---|---|
| drift | eval | NVIDIA-Nemotron-3-Nano-30B-A3B | - | 7 | 14 | 3/14 (21%) (P 0.54 / R 1.00) | – | 6.9 s | $0.00083 |
| drift | eval | Nemotron-3_5-Lightning | - | 7 | 14 | 14/14 (100%) (P 1.00 / R 1.00) | – | 8.6 s | $0.00075 |

## Gate outcomes (triage)

What the gate did with each verdict. A false rollback replaces live results with the certified copy and alerts an official; a missed tampering leaves tampered numbers live until the official's sign-off review.

| Split | Model | Gate | False rollbacks (legitimate or uncertain cases) | Tampering sent to sign-off as legitimate | Escalations (all runs) |
|---|---|---|---|---|---|

## Per case

| Suite | Case | Model | Gate | Expected | Got (per repeat) |
|---|---|---|---|---|---|
| drift | D1 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | none | ❌ vi:drop_box_close, vi:polls_close / ❌ vi:certification_date |
| drift | D1 | Nemotron-3_5-Lightning | - | none | ✅ none / ✅ none |
| drift | D2 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | es:polls_close, tl:election_day, vi:polling_place_site | ❌ es:polls_close, tl:election_day, vi:polling_place_site, vi:polls_close / ✅ es:polls_close, tl:election_day, vi:polling_place_site |
| drift | D2 | Nemotron-3_5-Lightning | - | es:polls_close, tl:election_day, vi:polling_place_site | ✅ es:polls_close, tl:election_day, vi:polling_place_site / ✅ es:polls_close, tl:election_day, vi:polling_place_site |
| drift | D3 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | es:phone, vi:certification_date | ❌ en:registration_site, es:phone, es:polling_place_site, vi:certification_date / ❌ en:registration_site, es:phone, vi:certification_date |
| drift | D3 | Nemotron-3_5-Lightning | - | es:phone, vi:certification_date | ✅ es:phone, vi:certification_date / ✅ es:phone, vi:certification_date |
| drift | D4 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | tl:drop_box_addresses, vi:drop_box_close | ❌ tl:drop_box_addresses, tl:drop_box_close, vi:drop_box_close, vi:polls_close / ❌ en:registration_site, tl:drop_box_addresses, vi:drop_box_close |
| drift | D4 | Nemotron-3_5-Lightning | - | tl:drop_box_addresses, vi:drop_box_close | ✅ tl:drop_box_addresses, vi:drop_box_close / ✅ tl:drop_box_addresses, vi:drop_box_close |
| drift | D5 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | none | ❌ vi:certification_date / ✅ none |
| drift | D5 | Nemotron-3_5-Lightning | - | none | ✅ none / ✅ none |
| drift | D6 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | es:registration_site, tl:service_centers_open | ❌ en:registration_site, es:registration_site, tl:service_centers_open, vi:polls_close / ❌ es:registration_site, tl:service_centers_open, vi:drop_box_close, vi:polls_close |
| drift | D6 | Nemotron-3_5-Lightning | - | es:registration_site, tl:service_centers_open | ✅ es:registration_site, tl:service_centers_open / ✅ es:registration_site, tl:service_centers_open |
| drift | D7 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | en:certification_date | ✅ en:certification_date / ❌ en:certification_date, vi:drop_box_close, vi:polls_close |
| drift | D7 | Nemotron-3_5-Lightning | - | en:certification_date | ✅ en:certification_date / ✅ en:certification_date |
