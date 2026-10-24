# Eval results (2026-10-24)

Repeats per case and model: 2. Temperature 0. Triage prompt SHA-256 `588f117b4a2d…`. Small fixture sets: read these as a sanity check, not a benchmark. Latency is wall-clock per run with 4 runs in flight at once (drift runs its 4 language extractions in parallel); a run that ends in an error still counts as wrong.

## Summary

Triage "verdict accuracy" scores the first verdict; "decision correct" scores what the gate did.

| Suite | Split | Model | Gate | Cases | Runs | Verdict accuracy | Decision correct | Median latency | Mean cost/run |
|---|---|---|---|---|---|---|---|---|---|
| drift | eval | NVIDIA-Nemotron-3-Nano-30B-A3B | - | 7 | 14 | 0/14 (0%) (P 0.43 / R 1.00) | – | 6.4 s | $0.00083 |
| drift | eval | Nemotron-3_5-Lightning | - | 7 | 14 | 5/14 (36%) (P 0.67 / R 1.00) | – | 4.2 s | $0.00076 |

## Gate outcomes (triage)

What the gate did with each verdict. A false rollback replaces live results with the certified copy and alerts an official; a missed tampering leaves tampered numbers live until the official's sign-off review.

| Split | Model | Gate | False rollbacks (legitimate or uncertain cases) | Tampering sent to sign-off as legitimate | Escalations (all runs) |
|---|---|---|---|---|---|

## Per case

| Suite | Case | Model | Gate | Expected | Got (per repeat) |
|---|---|---|---|---|---|
| drift | D1 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | none | ❌ vi:mail_ballots_sent / ❌ vi:mail_ballots_sent, vi:polls_close |
| drift | D1 | Nemotron-3_5-Lightning | - | none | ✅ none / ✅ none |
| drift | D2 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | es:polls_close, tl:election_day, vi:polling_place_site | ❌ en:registration_site, es:polls_close, tl:election_day, vi:mail_ballots_sent, vi:polling_place_site, vi:polls_close / ❌ en:registration_site, es:polls_close, tl:election_day, vi:polling_place_site |
| drift | D2 | Nemotron-3_5-Lightning | - | es:polls_close, tl:election_day, vi:polling_place_site | ❌ es:election_day, es:polls_close, tl:election_day, vi:mail_ballots_sent, vi:polling_place_site / ❌ es:polls_close, tl:election_day, vi:mail_ballots_sent, vi:polling_place_site |
| drift | D3 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | es:phone, vi:certification_date | ❌ en:registration_site, es:phone, vi:certification_date, vi:mail_ballots_sent / ❌ en:registration_site, es:phone, vi:certification_date, vi:mail_ballots_sent |
| drift | D3 | Nemotron-3_5-Lightning | - | es:phone, vi:certification_date | ❌ es:phone, vi:certification_date, vi:mail_ballots_sent / ❌ es:phone, vi:certification_date, vi:mail_ballots_sent |
| drift | D4 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | tl:drop_box_addresses, vi:drop_box_close | ❌ en:registration_site, tl:drop_box_addresses, vi:drop_box_close / ❌ en:registration_site, es:polling_place_site, tl:drop_box_addresses, vi:certification_date, vi:drop_box_close, vi:mail_ballots_sent |
| drift | D4 | Nemotron-3_5-Lightning | - | tl:drop_box_addresses, vi:drop_box_close | ❌ tl:drop_box_addresses, vi:drop_box_close, vi:mail_ballots_sent / ❌ tl:drop_box_addresses, vi:drop_box_close, vi:mail_ballots_sent |
| drift | D5 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | none | ❌ vi:certification_date, vi:mail_ballots_sent / ❌ en:registration_site |
| drift | D5 | Nemotron-3_5-Lightning | - | none | ✅ none / ✅ none |
| drift | D6 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | es:registration_site, tl:service_centers_open | ❌ es:registration_site, tl:service_centers_open, vi:mail_ballots_sent / ❌ es:registration_site, tl:service_centers_open, vi:mail_ballots_sent |
| drift | D6 | Nemotron-3_5-Lightning | - | es:registration_site, tl:service_centers_open | ✅ es:registration_site, tl:service_centers_open / ❌ es:registration_site, tl:service_centers_open, vi:mail_ballots_sent |
| drift | D7 | NVIDIA-Nemotron-3-Nano-30B-A3B | - | en:certification_date | ❌ en:certification_date, en:registration_site, es:polling_place_site, vi:mail_ballots_sent / ❌ en:certification_date, en:registration_site, vi:certification_date, vi:mail_ballots_sent |
| drift | D7 | Nemotron-3_5-Lightning | - | en:certification_date | ❌ en:certification_date, vi:mail_ballots_sent / ❌ en:certification_date, vi:mail_ballots_sent |
