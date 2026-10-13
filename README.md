# ASSAY-002

Pre-registered measurement of `subq-snap-preview` decision probabilities on Banking77 and CLINC150. Protocol: `PROTOCOL.md`. Report: `REPORT.md`. Gate: `GATE.md`. Runner receipt: `TOPH-ASSAY-002-RUN-RECEIPT-2026-10-12.md`.

- Freeze commit (pre-registered): `a161a41` — freeze hash `ab6a3ed265b6ae8bf3602e99315cf8eb46e3a365e2a327230fa71ac769b75f43`
- Current freeze manifest (with AMENDMENT-1 and AMENDMENT-2): `FREEZE.sha256`, hash `2bc47eea700f0af974853f3e46680b6a52ff3e4e99834c03889c5e202a824373`
- Verify: `shasum -a 256 -c FREEZE.sha256` → 14/14 OK

## Re-run block

From the repo root, with Python 3.9+ and numpy:

```sh
# verify the freeze and the seals
shasum -a 256 -c FREEZE.sha256
for d in raw/pass1 raw/pass2 raw/pass3 raw/order-probe; do
  for c in banking77 clinc150; do
    [ -f "$d/$c/responses.sha256" ] && (cd "$d/$c" && shasum -a 256 -c responses.sha256)
  done
done
for c in banking77 clinc150; do (cd "raw/drift/start/$c" && shasum -a 256 -c responses.sha256); (cd "raw/drift/end/$c" && shasum -a 256 -c responses.sha256); done

# primary scorer (harness/score.py, frozen sha 1141cd2c…)
python3 harness/score.py score raw/pass1/banking77/responses.jsonl labels/banking77.json
python3 harness/score.py score raw/pass1/clinc150/responses.jsonl labels/clinc150.json
python3 harness/score.py headline --input scores/banking77-pass1.json scores/banking77-pass2.json scores/banking77-pass3.json

# controls (must PASS before trusting any score)
python3 harness/controls.py

# independent re-scorer (rescore-bulma/, written blind from SPEC-FOR-INDEPENDENT-SCORER.md)
python3 rescore-bulma/rescore.py raw/pass1/banking77/responses.jsonl labels/banking77.json
python3 rescore-bulma/pairs.py raw/order-probe/banking77/responses.jsonl raw/order-probe/banking77/responses.jsonl O S
python3 rescore-bulma/controls.py
```

`raw/smoke/` is excluded from all scoring (§8). `raw/models/` is the key-check response only. No API key is needed to re-score; the key was only ever read by `harness/run.py` from `~/.config/subq/api_key` (mode 0600) and never appears in this repo.
