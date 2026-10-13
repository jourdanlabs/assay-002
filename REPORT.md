# ASSAY-002: SubQ Snap — a pre-registered measurement of decision probabilities (DRAFT — pending final close and Captain's publication call)

Engagement 002 in the ASSAY series. Subject: `subq-snap-preview` (Subquadratic's decision model), measured as served between **2026-10-12T22:09:13-05:00** and **2026-10-12T22:42:36-05:00** (America/Chicago), from Dallas, TX. Protocol, freeze, amendments, raw records, scorers, controls, receipts: this repository.

**Pre-registration.** The SHA-256 of the freeze manifest, `ab6a3ed265b6ae8bf3602e99315cf8eb46e3a365e2a327230fa71ac769b75f43` (freeze commit `a161a41`), was posted publicly before the first API call: on `donttrustme.ai/assay-002.html` (verified live serving the hash at 2026-10-12 22:06:02 -0500, and again on 2026-10-12 23:13 -0500) and as the public GitHub repo `github.com/jourdanlabs/assay-002` at `a161a41` (created 22:04 -0500; `git ls-remote` verified then and again 23:13 -0500). The first API call was 2026-10-12T22:08:48-05:00. Post-AMENDMENT-2 freeze hash: `2bc47eea700f0af974853f3e46680b6a52ff3e4e99834c03889c5e202a824373`.

**Roles.** Protocol author: Pan (Claude). Independent pre-freeze protocol review: none on record — a non-Claude read of the protocol was in flight at freeze time (Bulma/ChatGPT, uploaded 21:27) and had not landed before the hash was posted; the blind re-score covers scoring, not design. Runner: Toph (Grok). Blind independent re-scorer: Bulma (GPT). Third cross-check: Tifa's ASSAY-001 `rescore.py` (pinned). Gate: Pan. Final close: Pan (Claude, home). Call: Captain.

There was no vendor claim to test. This is a measurement report.

## The registered sentences (§7, generated mechanically by the frozen scorer)

> **On Banking77, Snap's chosen-option probabilities measured ECE 0.0335 (pass 1; 0.0328–0.0335 over three passes), inside the 0.05 line ASSAY-001 used.**
>
> **On CLINC150, Snap's chosen-option probabilities measured ECE 0.0560 (pass 1; 0.0559–0.0560 over three passes), outside the 0.05 line ASSAY-001 used, underconfident in every bin with at least 50 items (pass-1 95% interval 0.0491–0.0630 includes 0.05).**
>
> **Across 25,730 responses there were zero type errors under the checks ASSAY-001 used.**

Both corpora are public and old and both appear in Snap's own launch table, so accuracy is reported, not judged.

*A result applies to the artifacts and criteria examined: `subq-snap-preview` as served between the window above (response `model` values: `subq-snap-preview` only), Choice questions with null option descriptions in ASSAY-001's option order, these two corpora, and the docs pages hashed at freeze. It is not a statement about Snap on any other task, question type, corpus, context length or day.*

## M1 — calibration

| Corpus | Pass | n scored | Accuracy | Mean p | Signed gap | ECE10 | 95% interval | ECE equal-mass | Brier | Noise floor p95 | Direction (bins ≥50) |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---|
| Banking77 | 1 | 3,079 | 0.8058 | 0.8254 | +0.0196 | 0.0335 | 0.0240–0.0454 | 0.0334 | 0.2823 | 0.0198 | mixed |
| Banking77 | 2 | 3,080 | 0.8065 | 0.8255 | +0.0190 | 0.0328 | 0.0232–0.0446 | 0.0328 | 0.2821 | 0.0191 | mixed |
| Banking77 | 3 | 3,076 | 0.8059 | 0.8254 | +0.0195 | 0.0334 | 0.0242–0.0454 | 0.0325 | 0.2824 | 0.0198 | mixed |
| CLINC150 | 1 | 5,496 | 0.9092 | 0.8532 | −0.0560 | 0.0560 | 0.0491–0.0630 | 0.0560 | 0.1522 | 0.0136 | under |
| CLINC150 | 2 | 5,499 | 0.9094 | 0.8534 | −0.0560 | 0.0560 | 0.0491–0.0631 | 0.0560 | 0.1520 | 0.0136 | under |
| CLINC150 | 3 | 5,500 | 0.9093 | 0.8533 | −0.0559 | 0.0559 | 0.0491–0.0627 | 0.0559 | 0.1521 | 0.0134 | under |

All six passes sit above their noise floors. MCE over bins with n ≥ 50: 0.117–0.121 (Banking77), 0.152–0.158 (CLINC150). Probability sums: zero records off by more than 1e-3 across both corpora and all passes; every sum within 0.02. Zero `choice`-not-argmax exceptions in all six passes. Zero records with probability exactly 1.0 (the "1.00 atom" share is 0).

## M2 — type errors

Zero violations of any of checks (a)–(h) across 25,730 status-200 decision responses (three passes, both corpora): documented shape held everywhere; undocumented-only checks (sum within 0.02, confidence in [0,1]) also held everywhere.

## M3 — latency (an observation, Dallas, TX)

| Corpus | Pass | Median ms | p95 | p99 |
|---|---|---:|---:|---:|
| Banking77 | 1 | 265.0 | 306.3 | 324.2 |
| Banking77 | 2 | 267.5 | 324.8 | 452.0 |
| Banking77 | 3 | 272.5 | 350.1 | 428.0 |
| CLINC150 | 1 | 272.4 | 359.4 | 510.8 |
| CLINC150 | 2 | 272.5 | 331.5 | 431.7 |
| CLINC150 | 3 | 269.8 | 306.7 | 339.2 |

## Probes

**P1 — pass-to-pass stability.** Banking77: 2/3,079 flips (p1↔p2), 2/3,079 (p1↔p3), 4/3,076 (p2↔p3). CLINC150: 3/5,495, 0/5,496, 3/5,499. All flips had p < 0.9 on both sides. Item ids: `scores/finding-item-ids.json`.

**P2 — option order (650 paired calls, Banking77).** With the 77 options shuffled, Snap changed its answer on **35 of 300** items (all 35 had p < 0.9 on both sides; median |Δp| on stable items 0.0297; |Δp| > 0.05 on 38.5% of stable items; 40 pairs crossed the 0.9 line). Re-asked in the original order: **0 of 50** changed. Item ids: `scores/finding-item-ids.json`.

**P3 — out-of-scope readout (CLINC150, pass 1).** OOS accuracy 0.830 vs in-scope 0.9268; mean chosen-option p 0.7414 (OOS) vs 0.8781 (in-scope); AUROC 0.8057. High-confidence wrong answers on OOS items (p > 0.9, incorrect): 2.7% of OOS.

**P4 — the top bin and the 0.9 floor.** Ship-if-p>0.9: Banking77 ships 50.7% and is right 96.4% of the time (wrong shipped drops 598 → 56; 49.3% refused). CLINC150 ships 57.7%, right 97.3% (wrong shipped 499 → 84; 42.3% refused). Zero 1.00-probability atoms in any pass.

**P5 — drift.** 50 matched items per corpus at window start and end (~34 minutes apart, same model string): 0/50 changed answers in both corpora; median |Δp| 0.0; zero crossings of the 0.9 line.

**Secondary — Snap's `confidence` field.** Confidence ECE: 0.031 (Banking77 p1), 0.057 (CLINC150 p1). Monotone accuracy over confidence deciles: Banking77 no, CLINC150 yes. Reported, never gated.

## Historical reference (not a head-to-head)

Each number below is labeled: **historical reference: Jev, `jev-latest` → `jev-1.13.0`, single pass, 2026-09-17. Different model, date and version. Not a head-to-head.** Computed by the ASSAY-002 scorer from ASSAY-001's sealed files; no call was made to Jev's API.

| Corpus | Accuracy | ECE10 | 95% interval | Brier | 1.00-atom share | p>0.9 share |
|---|---:|---:|---|---:|---:|---:|
| Banking77 | 0.7977 | 0.0936 | 0.0815–0.1062 | 0.3088 | 0.4065 | 0.6912 |
| CLINC150 | 0.8812 | 0.0204 | 0.0184–0.0301 | 0.1846 | 0.4223 | 0.7027 |

## The run

26,596 decision records plus one `GET /v1/models`: 26,586 status 200, 10 status 0 (`ETIMEDOUT`, no retry, per the frozen retry rule; every step completed its planned n; item ids in `scores/finding-item-ids.json`). 20,855,282 input tokens against a 60,000,000 pre-registered cap (34.8%; pre-run projection 20,879,478). Listed-price cost $1.0428 at $0.05/M. Wall clock 33 min 48.5 s. Four workers; no circuit-breaker trip; no 401/402/403. All 13 step seals verify. Docs re-captured post-run: all eight pages hash-match the freeze. Host: Captain's Mac, Dallas, TX.

**Deviations (see AMENDMENT-2):** the session's default route was Wi-Fi (`en0`); the frozen OPEN-4 resolution said wired. AMENDMENT-2 records the departure, changes no text, rule, tolerance or headline, and assesses materiality (none found: the wired rule exists to avoid losses; losses were 0.038%, disclosed, with the disclosure remedy executed). The freeze hash changed accordingly; re-post of the updated hash accompanies publication.

## Verification

- **Positive controls** (the scorer must be able to fail): PASS under the frozen scorer before scoring, re-run PASS after the run (`controls/`); the independent re-scorer's own controls also PASS.
- **Blind independent re-score** (§15): Bulma (GPT-class seat, fresh context, blind to all numbers here) wrote her own scorer from the frozen spec. Pan re-ran her code from the sealed files: 16/16 outputs byte-identical; **891 shared metric fields, 0 differences** (counts exact, floats ±0.001, latency ±0.1 ms).
- **Third cross-check:** Tifa's ASSAY-001 `rescore.py` (pinned `477d86a7…`) on all six passes: 66/66 comparable fields exact.
- **Gate:** `GATE.md` (interim READY; final close and publication call are recorded there).

## What may not be said about this report

Per §7.5: no unqualified "Snap is/isn't calibrated"; no "first"; no better/worse claims against Jev or any model; vendor numbers never cited as independent; accuracy is not a quality verdict; nothing about Noul, Score, long context, images, other corpora or other days; no number from a pass or probe that did not run.

## Reproduce

See `README.md` for the re-run block. Every scorer output in this report is reproducible from `raw/` + `labels/` + the frozen spec by two independent codebases, both committed here.
