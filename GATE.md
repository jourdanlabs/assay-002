# GATE.md — ASSAY-002 §15 gate — 2026-10-12 (INTERIM — final close routes to Pan-on-Claude)

**Gate:** Pan (coordinator seat, interim). **Verdict: interim READY.** Nothing publishes on this verdict: publication is Captain's call (§16), after the final close and the OPEN-7 legal read.

## What was gated

The run at `b022682`, Pan's score layer at `561a5c8`, Bulma's blind re-score at `c316ee3`, AMENDMENT-2 at `393d928`. Branch `toph/assay-002-freeze-prep`. Nothing pushed.

## §15 checklist, worked from the files

1. **Re-hash corpus, freeze, docs and run seals.** `shasum -a 256 -c FREEZE.sha256`: **14/14 OK** (12 frozen + AMENDMENT-1 + AMENDMENT-2). Nested `CORPUS.sha256` and `DOCS.sha256` verified at freeze time; docs re-capture 8/8 MATCH. All 13 decision-step `responses.jsonl` seals recomputed independently: file hash = seal file = manifest, **13/13 OK**. Freeze hash now `2bc47eea700f0af974853f3e46680b6a52ff3e4e99834c03889c5e202a824373` (post-AMENDMENT-2); pre-registered public hash at freeze was `ab6a3ed265b6ae8bf3602e99315cf8eb46e3a365e2a327230fa71ac769b75f43`.
2. **Re-ran the re-scorer's code rather than trusting her JSON.** Bulma's `rescore.py` (`d1067bda…`), `pairs.py` (`9b32eac3…`), `controls.py` (`c7c4ef24…`) — hashes match her receipt. All 16 committed outputs (6 pass scores + 10 pair files) re-executed from the sealed raw files under my hand: **16/16 byte-identical** to her committed JSON.
3. **Δ table, field by field, each corpus, pass and probe.** Recursive leaf comparison over every shared field: **891 shared leaf fields, 0 differences** (floats ±0.001, latency ±0.1 ms, counts exact — no tolerance was needed; agreement was exact at the reported precision). Her spec decisions (RESCORE.md §deviations) are documented; decision 1 (pairs label-set check operationalized via probability keys) is empirically equivalent on the sealed records — every pair output matches byte-for-byte a scorer that had the label file.
4. **Controls pass under the final scorer.** Pan's `controls.py` re-run post-run: **PASS 52/52**, scorer sha `1141cd2c…` unchanged from freeze. Bulma's own controls re-run under my hand: **PASS** (uniform/overconfident/oracle at exact corpus n; 8/8 schema breaks caught; rounded-sums behavior as specified; shuffle-invariance byte-identical; pairs-self 0; pairs-mutated exactly 7; seed determinism byte-identical incl. bootstrap and noise floor).
5. **Manifests against §8.4.** 13 decision manifests: `"completed": true`, freeze commit `a161a41`, freeze file hash `ab6a3ed2…`, workers 4→4 (key-check 1→1 by harness design), zero circuit-breaker trips, no `stop_reason`, no 401/402/403. Record shape per §8.4 verified in smoke and pass files.
6. **Receipt accounting (§17).** Present: protocol/freeze files incl. amendments; labels/corpus/harness; controls with outputs; raw data incl. `raw/models` (key-check; no `responses.sha256` by harness design, disclosed) and `docs-recapture/`; `scores/` with reliability PNGs; `scores/jev-reference/`; `rescore-bulma/`; this GATE.md; `REPORT.md`; `README.md` re-run block. Every file in the repo is explained by this list or by `RECEIPT-PREP.md`.

## Third cross-check (§11)

Tifa's ASSAY-001 `rescore.py`, pinned sha256 `477d86a77f1a4d177fc1198afaed2be29e00452b289c12d2f965ac080f58496e` (re-verified), run by Pan on all six pass files, compared only on fields where its rules match Appendix A: **66/66 fields exact, 0 differences** (`third-check-tifa-rescore/DELTA.md`).

## Departures and their dispositions

| Departure | Disposition |
|---|---|
| Host ran on Wi-Fi `en0`; frozen OPEN-4 says wired | **AMENDMENT-2** (post-run, changes no text/rule/headline; materiality assessed: 10 losses, 0.038%, disclosure remedy already executed). Explained, per §13. |
| 10 status-0 `ETIMEDOUT` records, no retry | Not a departure: §8.3 says network errors are not retried; steps completed planned n; disclosed with item ids (`b77-2792`, `b77-0364`–`b77-0367`, `c150-0510`–`c150-0513`, `c150-4279`). |
| Smoke probabilities 14–20 decimals (docs examples show 1/0, 2 decimals) | Not a departure: §8 step 3 window opens only if precision is *coarser* than 2 decimals; it was finer; window did not open. |
| `raw/models/` has no `responses.sha256` | Harness design (key-check writes `response.json`); disclosed in runner receipt; §17 lists the directory, not a seal for it. |
| Blind re-score attempt 1 compromised (coordinator log leak), HOLD self-reported | Remediated out-of-band: attempt-1 outputs quarantined uncommitted outside the repo; fresh blind context produced `rescore-bulma/`; her blindness receipt is explicit; the compromised attempt never entered the repo. The Δ above is against the clean attempt only. |

## Open items before publication (all Captain's)

- Final close: Pan-on-Claude re-read of this gate and REPORT.md.
- **OPEN-7 / Chuck:** full terms read before publication; "no fitted recalibration" was honored — none exists in any output.
- "Assay" name collision clearance (Captain's list).
- Visible re-post of the updated freeze hash `2bc47eea…` (AMENDMENT-2 changes it), per OPEN-6 — Captain posts, no agent.
- Publication itself (§16).

## Interim verdict

**READY** — the score layer, the re-score, the controls, the seals, the receipts and the amendment trail are internally consistent and reproducible from the files. This verdict authorizes nothing public. Final close: Pan-on-Claude. Publication: Captain.
