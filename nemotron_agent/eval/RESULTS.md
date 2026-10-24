# Eval results (2026-10-24)

Repeats per case and model: 2. Temperature 0. Triage prompt SHA-256 `588f117b4a2d…`. Small fixture sets: read these as a sanity check, not a benchmark. Latency is wall-clock per run with 4 runs in flight at once (drift runs its 4 language extractions in parallel); a run that ends in an error still counts as wrong.

## Summary

| Suite | Split | Model | Cases | Runs | Correct | Accuracy | Median latency | Mean cost/run |
|---|---|---|---|---|---|---|---|---|
| drift | eval | NVIDIA-Nemotron-3-Nano-30B-A3B | 7 | 14 | 3 | 21% (P 0.57 / R 1.00) | 7.6 s | $0.00083 |
| drift | eval | Nemotron-3_5-Lightning | 7 | 14 | 14 | 100% (P 1.00 / R 1.00) | 4.0 s | $0.00077 |
| triage | dev | NVIDIA-Nemotron-3-Nano-30B-A3B | 8 | 16 | 9 | 56% | 8.6 s | $0.00055 |
| triage | dev | Nemotron-3_5-Lightning | 8 | 16 | 10 | 62% | 18.2 s | $0.00152 |
| triage | dev | nemotron-3-super-120b-a12b | 8 | 16 | 13 | 81% | 7.2 s | $0.00127 |
| triage | heldout | NVIDIA-Nemotron-3-Nano-30B-A3B | 7 | 14 | 11 | 79% | 12.8 s | $0.00065 |
| triage | heldout | Nemotron-3_5-Lightning | 7 | 14 | 10 | 71% | 24.5 s | $0.00153 |
| triage | heldout | nemotron-3-super-120b-a12b | 7 | 14 | 11 | 79% | 9.5 s | $0.00147 |

## Gate outcomes (triage)

What the gate did with each verdict. A false rollback replaces live results with the certified copy and alerts an official; a missed tampering leaves tampered numbers live until the official's sign-off review.

| Split | Model | False rollbacks (legitimate or uncertain cases) | Tampering sent to sign-off as legitimate |
|---|---|---|---|
| dev | NVIDIA-Nemotron-3-Nano-30B-A3B | 6 of 8 | 1 of 8 |
| dev | Nemotron-3_5-Lightning | 2 of 8 | 0 of 8 |
| dev | nemotron-3-super-120b-a12b | 1 of 8 | 0 of 8 |
| heldout | NVIDIA-Nemotron-3-Nano-30B-A3B | 2 of 10 | 1 of 4 |
| heldout | Nemotron-3_5-Lightning | 4 of 10 | 0 of 4 |
| heldout | nemotron-3-super-120b-a12b | 2 of 10 | 1 of 4 |

## Per case

| Suite | Case | Model | Expected | Got (per repeat) |
|---|---|---|---|---|
| drift | D1 | NVIDIA-Nemotron-3-Nano-30B-A3B | none | ✅ none / ❌ en:registration_site |
| drift | D1 | Nemotron-3_5-Lightning | none | ✅ none / ✅ none |
| drift | D2 | NVIDIA-Nemotron-3-Nano-30B-A3B | es:polls_close, tl:election_day, vi:polling_place_site | ❌ es:polling_place_site, es:polls_close, tl:election_day, vi:polling_place_site / ✅ es:polls_close, tl:election_day, vi:polling_place_site |
| drift | D2 | Nemotron-3_5-Lightning | es:polls_close, tl:election_day, vi:polling_place_site | ✅ es:polls_close, tl:election_day, vi:polling_place_site / ✅ es:polls_close, tl:election_day, vi:polling_place_site |
| drift | D3 | NVIDIA-Nemotron-3-Nano-30B-A3B | es:phone, vi:certification_date | ❌ en:registration_site, es:phone, vi:certification_date / ❌ en:registration_site, es:phone, vi:certification_date |
| drift | D3 | Nemotron-3_5-Lightning | es:phone, vi:certification_date | ✅ es:phone, vi:certification_date / ✅ es:phone, vi:certification_date |
| drift | D4 | NVIDIA-Nemotron-3-Nano-30B-A3B | tl:drop_box_addresses, vi:drop_box_close | ❌ en:registration_site, tl:drop_box_addresses, vi:drop_box_close, vi:polls_close / ❌ es:polling_place_site, tl:drop_box_addresses, vi:drop_box_close, vi:polls_close |
| drift | D4 | Nemotron-3_5-Lightning | tl:drop_box_addresses, vi:drop_box_close | ✅ tl:drop_box_addresses, vi:drop_box_close / ✅ tl:drop_box_addresses, vi:drop_box_close |
| drift | D5 | NVIDIA-Nemotron-3-Nano-30B-A3B | none | ❌ vi:certification_date / ❌ tl:drop_box_close, vi:drop_box_addresses |
| drift | D5 | Nemotron-3_5-Lightning | none | ✅ none / ✅ none |
| drift | D6 | NVIDIA-Nemotron-3-Nano-30B-A3B | es:registration_site, tl:service_centers_open | ❌ en:registration_site, es:registration_site, tl:service_centers_open, vi:certification_date / ❌ en:registration_site, es:registration_site, tl:service_centers_open |
| drift | D6 | Nemotron-3_5-Lightning | es:registration_site, tl:service_centers_open | ✅ es:registration_site, tl:service_centers_open / ✅ es:registration_site, tl:service_centers_open |
| drift | D7 | NVIDIA-Nemotron-3-Nano-30B-A3B | en:certification_date | ✅ en:certification_date / ❌ en:certification_date, vi:certification_date |
| drift | D7 | Nemotron-3_5-Lightning | en:certification_date | ✅ en:certification_date / ✅ en:certification_date |
| triage | H01 | NVIDIA-Nemotron-3-Nano-30B-A3B | legitimate | ✅ legitimate 0.93 / ✅ legitimate 0.93 |
| triage | H01 | Nemotron-3_5-Lightning | legitimate | ❌ tampering 0.85 / ❌ tampering 0.84 |
| triage | H01 | nemotron-3-super-120b-a12b | legitimate | ❌ tampering 0.92 / ✅ legitimate 0.85 |
| triage | H02 | NVIDIA-Nemotron-3-Nano-30B-A3B | legitimate | ✅ legitimate 0.93 / ✅ legitimate 0.93 |
| triage | H02 | Nemotron-3_5-Lightning | legitimate | ✅ legitimate 0.95 / ✅ legitimate 0.94 |
| triage | H02 | nemotron-3-super-120b-a12b | legitimate | ✅ legitimate 0.95 / ✅ legitimate 0.95 |
| triage | H03 | NVIDIA-Nemotron-3-Nano-30B-A3B | tampering | ✅ tampering 0.88 / ✅ tampering 0.92 |
| triage | H03 | Nemotron-3_5-Lightning | tampering | ✅ tampering 0.93 / ✅ tampering 0.91 |
| triage | H03 | nemotron-3-super-120b-a12b | tampering | ✅ tampering 0.91 / ✅ tampering 0.96 |
| triage | H04 | NVIDIA-Nemotron-3-Nano-30B-A3B | legitimate | ✅ legitimate 0.96 / ✅ legitimate 0.93 |
| triage | H04 | Nemotron-3_5-Lightning | legitimate | ✅ legitimate 0.95 / ✅ legitimate 0.95 |
| triage | H04 | nemotron-3-super-120b-a12b | legitimate | ✅ legitimate 0.90 / ✅ legitimate 0.95 |
| triage | H05 | NVIDIA-Nemotron-3-Nano-30B-A3B | tampering | ✅ tampering 0.88 / ❌ legitimate 0.93 |
| triage | H05 | Nemotron-3_5-Lightning | tampering | ✅ tampering 0.88 / ✅ tampering 0.88 |
| triage | H05 | nemotron-3-super-120b-a12b | tampering | ✅ tampering 0.86 / ❌ legitimate 0.95 |
| triage | H06 | NVIDIA-Nemotron-3-Nano-30B-A3B | legitimate | ✅ legitimate 0.96 / ✅ legitimate 0.96 |
| triage | H06 | Nemotron-3_5-Lightning | legitimate | ✅ legitimate 0.95 / ✅ legitimate 0.95 |
| triage | H06 | nemotron-3-super-120b-a12b | legitimate | ✅ legitimate 0.96 / ✅ legitimate 0.90 |
| triage | H07 | NVIDIA-Nemotron-3-Nano-30B-A3B | uncertain | ❌ tampering 0.92 / ❌ tampering 0.92 |
| triage | H07 | Nemotron-3_5-Lightning | uncertain | ❌ tampering 0.92 / ❌ tampering 0.93 |
| triage | H07 | nemotron-3-super-120b-a12b | uncertain | ✅ uncertain 0.60 / ❌ tampering 0.85 |
| triage | T01 | NVIDIA-Nemotron-3-Nano-30B-A3B | tampering | ✅ tampering 0.97 / ✅ tampering 0.96 |
| triage | T01 | Nemotron-3_5-Lightning | tampering | ✅ tampering 0.93 / ✅ tampering 0.96 |
| triage | T01 | nemotron-3-super-120b-a12b | tampering | ✅ tampering 0.95 / ✅ tampering 0.92 |
| triage | T02 | NVIDIA-Nemotron-3-Nano-30B-A3B | tampering | ✅ tampering 0.96 / ✅ tampering 0.96 |
| triage | T02 | Nemotron-3_5-Lightning | tampering | ✅ tampering 0.93 / ✅ tampering 0.94 |
| triage | T02 | nemotron-3-super-120b-a12b | tampering | ✅ tampering 0.95 / ✅ tampering 0.95 |
| triage | T03 | NVIDIA-Nemotron-3-Nano-30B-A3B | tampering | ❌ legitimate 0.96 / ✅ tampering 0.96 |
| triage | T03 | Nemotron-3_5-Lightning | tampering | ✅ tampering 0.94 / ✅ tampering 0.82 |
| triage | T03 | nemotron-3-super-120b-a12b | tampering | ❌ uncertain 0.60 / ✅ tampering 0.90 |
| triage | T04 | NVIDIA-Nemotron-3-Nano-30B-A3B | legitimate | ✅ legitimate 0.85 / ❌ tampering 0.92 |
| triage | T04 | Nemotron-3_5-Lightning | legitimate | ❌ error / ❌ error |
| triage | T04 | nemotron-3-super-120b-a12b | legitimate | ✅ legitimate 0.90 / ✅ legitimate 0.90 |
| triage | T05 | NVIDIA-Nemotron-3-Nano-30B-A3B | legitimate | ❌ tampering 0.94 / ❌ tampering 0.93 |
| triage | T05 | Nemotron-3_5-Lightning | legitimate | ❌ error / ❌ error |
| triage | T05 | nemotron-3-super-120b-a12b | legitimate | ✅ legitimate 0.95 / ✅ legitimate 0.95 |
| triage | T06 | NVIDIA-Nemotron-3-Nano-30B-A3B | legitimate | ✅ legitimate 0.93 / ❌ tampering 0.92 |
| triage | T06 | Nemotron-3_5-Lightning | legitimate | ✅ legitimate 0.92 / ✅ legitimate 0.95 |
| triage | T06 | nemotron-3-super-120b-a12b | legitimate | ✅ legitimate 0.95 / ✅ legitimate 0.95 |
| triage | T07 | NVIDIA-Nemotron-3-Nano-30B-A3B | uncertain | ❌ tampering 0.92 / ❌ tampering 0.93 |
| triage | T07 | Nemotron-3_5-Lightning | uncertain | ❌ tampering 0.92 / ❌ tampering 0.88 |
| triage | T07 | nemotron-3-super-120b-a12b | uncertain | ❌ tampering 0.85 / ❌ tampering 0.78 |
| triage | T08 | NVIDIA-Nemotron-3-Nano-30B-A3B | tampering | ✅ tampering 0.96 / ✅ tampering 0.96 |
| triage | T08 | Nemotron-3_5-Lightning | tampering | ✅ tampering 0.97 / ✅ tampering 0.97 |
| triage | T08 | nemotron-3-super-120b-a12b | tampering | ✅ tampering 0.95 / ✅ tampering 0.96 |
