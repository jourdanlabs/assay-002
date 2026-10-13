# RECEIPT-PREP — ASSAY-002 freeze preparation (accumulating)

Runner: Toph · Branch: `toph/assay-002-freeze-prep` · Protocol: `pan-cc/handoffs/assay-002-draft/PROTOCOL-DRAFT-2026-10-12.md` (Pan's rulings in the runner brief applied; science unchanged)
Environment observed: Python 3.9.6, numpy 2.0.2, pandas 2.3.3, pyarrow 21.0.0, matplotlib 3.9.4 (system Python, Captain's Mac).
**Zero Snap/Jev API calls made in prep. The key file was never read.**

## OPEN-13 (before freeze prep)

- `OPEN13-REVIEW.md` + `docs-open13/` at root commit `f74e7f3`. Verdict: nothing in the assigned unread set defines `confidence`, probability precision, or version pinning. Pan notified (`chamber-inbox/pan/20261012-195855-toph-assay002-open13.md`).

## §12.1 Corpora

Copied unchanged from `~/projects/assay-001/` (tracked files only): `corpus/banking77/{categories.json,test.csv}`, `corpus/clinc150/{README.md,test.parquet,intent_names.json}`, `CORPUS.sha256`, `PINS.txt`.

`shasum -a 256 -c CORPUS.sha256` from repo root:

```
corpus/banking77/categories.json: OK
corpus/banking77/test.csv: OK
corpus/clinc150/README.md: OK
corpus/clinc150/test.parquet: OK
corpus/clinc150/intent_names.json: OK
```

- `CORPUS.sha256` SHA-256: `25d113581f3191354ab3543d3450df18c97132189d5ab6c5a0f803b82d02dfd8`
- `PINS.txt` SHA-256: `962f61aca557ee9e8cfb6212cf92bb481905423c487bccef36ac776a832311c5`

## §12.2 Option lists

Generator: `prep/make_labels_perms.py` (stdlib only; sources = the verified copies above).

- `labels/banking77.json`: the 77 labels in `categories.json` order (asserted `list`, len 77). SHA-256 `d257e168e30e0605556d45a71eb41a556bdbf6d73276b449db255307f3de7f48`. Banking77 test rows counted: 3,080; every `category` in the label set.
- `labels/clinc150.json`: `[intent_names[str(i)] for i in 0..150]` (asserted 151 keys `0`–`150`, index 42 = `oos`). SHA-256 `c06d3c60f52659311549b6b2f26b9fc5d9e5428b548d970da5b8c37582ccb9c1`.
- Format: plain JSON array of label strings (the shape Appendix A `rescore.py` argv[2] specifies), `json.dumps(..., indent=1)` + newline.

## §12.3 Permutations

Construction (§6.2 verbatim): `rng = random.Random(20260920)`; for each of the first 300 Banking77 items in file order, `shuffled = labels[:]; rng.shuffle(shuffled)`.

- Verification target: `order_first5` of the 300 `shuffled` records in `assay-001/raw/permutation-2026-09-20/responses.jsonl` (line count 350 = 300 `shuffled` + 50 `original-again`).
- **Result: `order_first5 matched: 300/300`.** (Generator writes the file only on a full match; otherwise STOP.)
- `labels/b77-permutations-300.json`: `{"seed": 20260920, "n": 300, "items": [{"id": "b77-0000".."b77-0299", "options": [77 labels]}]}`. SHA-256 `1649eda0c7620b04327af28252a200ea2da690f28e15de2a326b1a629ded2172`.

## §12.4 Docs capture

Captured by unauthenticated public `curl -sSL` GETs from **2026-10-13T01:03:34Z to 2026-10-13T01:03:35Z**. `docs/CAPTURE.json` records the source URL, byte-preserving method where applicable, item hashes, and the comparison to Pan's 2026-10-12T23:58:07Z capture.

- `docs/decisions-api.md` exactly matched Pan's prior SHA-256 (`65fa1462…a774ea2`).
- `docs/llms.txt` exactly matched Pan's prior SHA-256 (`69f87742…5b21528`).
- Also captured `docs/models.md`, `docs/data-retention.md`, launch-post HTML + extracted text, and terms HTML + extracted text.
- Disclosure: the extracted launch-post text does **not** reproduce Pan's prior text hash (`9d25ea04…10b0d23` observed here versus `1583ec9c…3714c6a` in the draft). The prior extraction method was unavailable; the raw HTML (`25e968e0…b4f85d`) and this capture's exactly described extraction (`prep/open13_strip.py`) are both preserved. This is a byte-artifact mismatch requiring Pan's gate comparison; it is not silently treated as a match.
- `DOCS.sha256` covers all nine files in `docs/`, including `docs/CAPTURE.json`; `shasum -a 256 -c DOCS.sha256` reported **9/9 OK**. `DOCS.sha256` SHA-256: `1edfd8f6d246482728fb8414ccd7172a746a660af357ff5ae56e46c11d8862e2`.

## §12.5 Scorer spec

`SPEC-FOR-INDEPENDENT-SCORER.md` was extracted mechanically from the Appendix A fenced block by `prep/extract_spec.py`, without hand editing. Source draft SHA-256 `73587d0ea57e3480a9d5a0edd6b598653b4536072d0b1c607725090d2bfff78b`; extractor asserted the expected first/last content. Output: **7,030 bytes**, SHA-256 `d448ca7f83ffa1e276af032f70f7c7bca353d96774258d1a40f7e0854e3c994d`.

## §12.6 Harness

Starting copies were assay-001 `run.py` / `score.py` / `controls.py` (byte-identical at copy time); `permute.py` was not copied because its construction now lives in the frozen permutations file and the P2 step in `run.py`. Current SHA-256:

- `harness/run.py` `1faff62fe44b8b1e68900382ed48bfb41814e9b81271b633e7100877e164d22f`
- `harness/score.py` `1141cd2c1841f847ee7274ef1695351791a5bf2f47b1fbe63f4f7940f00c8e2a`
- `harness/pairs.py` `86915d66fa7d20067a8a8550bebe50dbbb4e0e01ee389e59ebe360c2717f545f`
- `harness/controls.py` `d1c581c7bbe9a111c6676a2ecc1a56217ddb0c82b05ee3f1561a5fb11da9c701`

`run.py` implements the registered key check, smoke, drift, three-pass and paired P2 steps; FREEZE/CORPUS/DOCS hash verification before a key load; protocol hash from `FREEZE.sha256`; §8.3 retries; 401/402/403 stop; rolling-100 circuit breaker (60 s pause, halved concurrency, trips in the manifest); the 60M running cap meter plus the §9 Rule-1 projection check before drift-start; required `--location`; and sealed per-step manifests. Offline fake-transport probes (`/tmp/assay2_run_tests.py`, not a shipped artifact) passed: 429→500→200 recorded attempts/retries with waits `[7, 2]` s (Retry-After honored), 403 and network errors were not retried, cap admission stopped at the cap, the breaker tripped once at 100/100 retry-needed completions, a 403 stopped later work, and P2 sent canonical then frozen-shuffled criteria. **No real API calls were made and the key was not loaded.**

## §12.7 / §14 Controls

Command: `python3 harness/controls.py` (seed 1). Final scorer SHA-256 `1141cd2c…00c8e2a`, tolerance **0.02**, recorded inside every per-control score output and in `controls/CONTROL-RESULTS.json` (SHA-256 `3c8297f4a54fb03bc9a6e4d175b5df72cfe39683ec09794136e4427ae8324b9e`).

Result: **PASS — 52/52 checks.** Banking77 / CLINC150 headline control values: uniform-random ECE 0.001 / 0.001, accuracy 0.014 / 0.0056; overconfident ECE 0.986 / 0.9944; perfect-oracle ECE 0.0 / accuracy 1.0; broken-schema caught exactly **29 / 59** injected breaks; rounded-sums designated **308 / 550** records at sum 0.99, counted by `sum_off_1e3`, with 0 violations at 0.02 and calibration n unchanged (3,080 / 5,500). Shuffle-invariance, seed determinism, pairs-self (0 flips) and pairs-mutated (exactly 17 flips per corpus) all passed. Synthetic control inputs, per-control score JSONs and pair outputs are under `controls/`.

## §12.8–12.9 Freeze candidate

- `PROTOCOL.md` is a byte-for-byte copy of Pan's reviewed draft (`pan-cc/handoffs/assay-002-draft/PROTOCOL-DRAFT-2026-10-12.md`); SHA-256 `73587d0ea57e3480a9d5a0edd6b598653b4536072d0b1c607725090d2bfff78b`. The runner changed none of its science or wording. It therefore still self-identifies as a draft and retains the original OPEN list; Pan's brief rulings were applied operationally in this prep (60M cap in code, repo path, OPEN-13) and are **not** rewritten into Pan's text here. Pan must accept or finalize that administrative state at the gate before any key load.
- `FREEZE.sha256` contains the 12 §12.8 entries (protocol, scorer spec, corpus/pins/docs manifests, 3 label files, 4 harness files). Verification: `shasum -a 256 -c FREEZE.sha256` → **12/12 OK**; `run.load_freeze()` also verified the nested CORPUS and DOCS manifests. `FREEZE.sha256` SHA-256: `390296ce5671f5cd1ea24053ab53c624b8d70fd9b58ce39e463d49d2b76ce629`.
- Offline dry runs after the manifest existed (`run.py --step key-check --dry-run`; `run.py banking77 --step smoke --dry-run`, location supplied on the command line) printed the registered request shapes, created no `raw/` output, loaded no key and sent nothing.
- The freeze-candidate commit is the commit introducing `FREEZE.sha256` with message `freeze: zero API calls made`; its hash and machine time are recorded in git and in the Pan handoff. **Status: awaiting Pan's freeze gate, then Captain's key/balance and hash-post decisions. No Snap or Jev API call has been made.**
