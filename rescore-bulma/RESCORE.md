# ASSAY-002 blind independent re-score — Bulma

## Blindness and scope receipt

I am a fresh context; I never saw attempt-1 outputs or Pan's numbers; boot
quarantine was followed.

I loaded the sanitized W42 session log, W41, and the shared memory index. I did not
open any ASSAY-002 scoring memory card. I did not open, read, list, hash, or stat
`scores/`, `third-check-tifa-rescore/`, `GATE.md`, or the attempt-1 quarantine. I
did not read or run any Pan scorer, pair script, harness, or control generator.
`rescore-bulma/` was created successfully as a fresh directory before work began.

The only ASSAY-002 inputs used were the frozen scorer spec, protocol context,
`labels/`, and sealed `raw/` response files. `raw/smoke/` and `raw/models/` were
not scored.

## Environment

- Python: 3.9.6
- NumPy: 2.0.2
- Platform: macOS Darwin 25.5.0
- Branch: `toph/assay-002-freeze-prep`
- Starting commit: `561a5c8c947f0122cbc5ac79a5a7f90db4a176bc`

## Scorer files

| File | SHA-256 |
|---|---|
| `rescore.py` | `d1067bda62ce43a42ba460f0ac9de456e107f783f6d76cb3eb6e4d8efe8d6949` |
| `pairs.py` | `9b32eac336d90b14bcedd1a1d8697b1493176d6c665d119ed8d8036dec28eed6` |
| `controls.py` | `c7c4ef24c429f7d68191d34258ea8d94003afb6bb77cfcd6a67ff9b20e7158c6` |

Both scorer CLIs print JSON only. The six score objects and ten pair objects use
the exact top-level key order from the frozen spec. All metric floats are rounded
to four decimals and latency fields to one decimal.

## Controls

Controls ran before any real scoring and passed. Full details are in
`CONTROLS.md` (SHA-256
`cd01b62159cf24b913b3e6eb55eca452992aa4ebbb530e392ad19b18341b4582`)
and `controls-results.json` (SHA-256
`4d71ce713bd57d7b7d52900752e516069e9b79f1162bc96d41ce14788d95d9f6`).

- Uniform-random, overconfident, and perfect-oracle controls covered the exact
  registered item count for each corpus.
- All eight injected schema breaks were caught.
- Rounded 0.99 sums stayed in calibration, were counted outside 1e-3, and passed
  the 0.02 tolerance.
- Shuffle invariance passed byte-for-byte.
- Pairs-self reported zero flips; pairs-mutated reported exactly the seven
  injected flips.
- Repeated seeded scoring was byte-identical, including bootstrap and noise
  outputs.

## Score output hashes

| Output | SHA-256 |
|---|---|
| `banking77-pass1.json` | `e43d98af39cee87cec6057f01daf87ff5f120f251326e6ea8a11c0dded31efcb` |
| `banking77-pass2.json` | `ddb151f7ecc5ee33eb504345860feb0f9813824d934aa8dcb5683dd9c547a729` |
| `banking77-pass3.json` | `3c3794e7e2acaf0412690ae2f60e0c52b0b1bd56db1d81fe61c805c00580ace9` |
| `clinc150-pass1.json` | `a9d8c8d99c2bc47fb20d0c28a260ba934e5ad18abce93e3503b8f86cc2891069` |
| `clinc150-pass2.json` | `46033175ffe8dda40df51b21459f3c1257c9f394e98fa3872552d142abb8590b` |
| `clinc150-pass3.json` | `aac70608169e866dca6d120cabd8195abc4b1a510c624e40ff1aaf733ff93a1b` |

## Pair output hashes

| Output | SHA-256 |
|---|---|
| `banking77-pass1-v-pass2.json` | `8830d7b46b7e802a0430fc3cf0f1bb6528a417eef3cda286436cbec249514a22` |
| `banking77-pass1-v-pass3.json` | `09e08416abc644020175528b9936a5bd2366ae5cfb9eea01108d347903efc375` |
| `banking77-pass2-v-pass3.json` | `bf8105bd152bb4f95a8ec11ecfc2096335f3e532d19ca74dabaae2f5064497f3` |
| `clinc150-pass1-v-pass2.json` | `503a97af8397c63f889601da84d6a4ba737f6f2c7c9ebac5ff751a094341d2fe` |
| `clinc150-pass1-v-pass3.json` | `0e300a9f34d3b60b0ee1bef253e9c1bd59591cdc8fcc614559c28b94108a3426` |
| `clinc150-pass2-v-pass3.json` | `c1282f13b0d5894a1206ee8566ce9f438ca325f0e2bdf8678f8ad6906c271f43` |
| `banking77-order-O-v-S.json` | `e25d426462cf0701cc740b74b7c1729b01ff6a04a73471547698a0dc8c224778` |
| `banking77-order-O-v-O2.json` | `aa938ee04b5d29573ffcfaab9bfc52ab4fbc14c76450d570aabe49a96b0858be` |
| `banking77-drift-start-v-end.json` | `81a88f658355805790dbe4c7a0afcdec46f37b3f6b209b0064f5ebf2d3083bef` |
| `clinc150-drift-start-v-end.json` | `574c9b837f1d727f21a0f16edaaa5ae96dae277b23b8306da554694561092103` |

The CLINC150 pass outputs include the requested `oos` readout with out-of-scope
label `oos`.

## Spec decisions and deviations

1. `pairs.py` has no label-file argument, although Q1 says to build the R3 set and
   R3 includes membership in a label set. I treated a string `choice` present in
   the record's probability object as the operational membership check. For the
   sealed records, whose probability keys are the exact option set, this is
   equivalent to R3. The script still enforces every other R3 inclusion rule.
2. The spec does not define handling for malformed or missing IDs used in sorting
   and joining. I use the string ID directly when valid and deterministic compact
   JSON text otherwise. No sealed calibration record needed this fallback.
3. The spec fixes top-level key order but not nested key spelling/order. I used
   the metric names from R12/R17 (`n`, `share`, `acc`, `wilson`;
   `wrong_all`, `wrong_shipped`, `right_share_shipped`, `refused_share`; and
   `AUROC`) in textual order.
4. Protocol §14 refers to Pan's request builder. The blind brief explicitly
   prohibited reading or executing Pan code, so the retained control generator
   constructs the frozen record shape directly from the scorer spec.

There were no metric-definition deviations.

## Verification

- Positive controls: PASS.
- Deterministic re-run against one file from each corpus and the O-v-S probe:
  byte-identical.
- Syntax parse: PASS.
- Output key-order check: six score files and ten pair files PASS.
- Scoped `git diff --check`: PASS.

This is an interim independent re-score, not a final gate or publication
clearance. Pan must re-run these files and build the field-by-field delta table
under §15.
