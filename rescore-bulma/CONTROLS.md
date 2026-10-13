# ASSAY-002 Bulma independent scorer controls

Status: **PASS**

The controls ran successfully before any sealed response file was scored. They were
generated with seed 1 in the record shape defined by
`SPEC-FOR-INDEPENDENT-SCORER.md`. No Pan harness or scorer code was read or run.
Synthetic IDs covered the full registered cardinality of both corpora: 3,080
Banking77 records and 5,500 CLINC150 records.

| Control | Banking77 | CLINC150 | Result |
|---|---:|---:|---|
| Uniform-random accuracy | 0.0136 | 0.0062 | PASS |
| Uniform-random ECE | 0.0006 | 0.0004 | PASS |
| Overconfident accuracy | 0.0136 | 0.0062 | PASS |
| Overconfident ECE | 0.9864 | 0.9938 | PASS |
| Perfect-oracle accuracy | 1.0000 | 1.0000 | PASS |
| Perfect-oracle ECE | 0.0000 | 0.0000 | PASS |

Additional controls:

- Broken schema: 8 of 8 injected breaks caught; 6 documented-shape and 2
  undocumented-only.
- Rounded sums: 20 records remained in calibration; 10 sums at 0.99 were counted
  outside 1e-3; zero violated the 0.02 tolerance.
- Shuffle invariance: byte-identical JSON output before and after deterministic
  record-order shuffling.
- Pairs-self: 0 flips.
- Pairs-mutated: exactly 7 injected flips reported.
- Seed determinism: byte-identical repeated output, including bootstrap interval
  `[0.0001, 0.0024]`, noise mean `0.0009`, and noise p95 `0.0021`.

The machine-readable receipt is `controls-results.json`. The retained generator is
`controls.py`; its temporary synthetic JSONL files were deleted automatically.
