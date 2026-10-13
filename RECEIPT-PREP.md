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

## Pending at this commit

§12.4 docs capture · §12.5 scorer spec · §12.6 harness edits · §12.7/§14 controls · §12.8 `FREEZE.sha256` · §12.9 freeze commit. Nothing runs before Pan gates the freeze.
