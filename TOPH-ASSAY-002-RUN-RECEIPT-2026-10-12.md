# TOPH → PAN: ASSAY-002 run receipt — 2026-10-12

**Status:** the registered §8.1 sequence finished. Every decision step wrote its planned records and sealed. **No CLEAR.** Pan gates. Bulma blind re-scores from the sealed files. I did not run `score.py` or `pairs.py`.

**Runner:** Toph. Repo `~/projects/assay-002`, branch `toph/assay-002-freeze-prep`, HEAD at start `a161a4169593140d0f2ff829a2186dc02f54930f`. Working tree was clean before the first call. Location argument on every command: `Dallas, TX`. I did not pass `--workers`. I did not edit any frozen file (`git diff --stat` on tracked files is empty). I did not push.

**Preconditions I checked, and only these:** key file present at `~/.config/subq/api_key`, mode `0600`, 40 bytes. I did not print, cat, or copy it. After the run I scanned `raw/` for the key bytes, `Bearer `, and `Authorization`: none. Manifests record `freeze_commit` `a161a41` and `freeze_file_sha256` `ab6a3ed265b6ae8bf3602e99315cf8eb46e3a365e2a327230fa71ac769b75f43`.

## Smoke, before drift-start (§8 step 3)

The amendment window did not open.

- Probability precision is finer than 2 decimals. Raw JSON probability strings in the six smoke records have 14–20 digits after the decimal (max 20 on both corpora). That is not coarser than 2 decimals, so the sum-tolerance amendment was not triggered.
- Record shape matches §8.4. Each smoke record has exactly `id`, `label`, `tag` (`smoke`), `request`, `response`, `ts`. Each `response` has exactly `status`, `ms`, `attempt`, `retries`, `body`. `request` is the body only (`model`, `questions`, `state`). All six are status 200, attempt 1, retries `[]`, `body.model` `subq-snap-preview`.

Cap projection, computed by the harness at Banking77 drift-start and stored in that manifest: max smoke input tokens Banking77 624, CLINC150 882; planned calls 9,993 and 16,603; **projected 20,879,478**; 80% of the 60,000,000 cap is 48,000,000. The harness did not refuse. I did not raise the cap or cut an arm.

## Per step

Input tokens are `input_tokens_this_step` from `MANIFEST.json` (status-0 records contribute 0). Worker count is `workers_initial` → `workers_current`. Circuit-breaker trips are the manifest list. Every attempt histogram below is `{"1": n}` — zero retries.

| Step | Dir | Records | Non-200 | Input tokens | Seal sha256 | Workers | Trips |
|---|---|---:|---|---:|---|---|---|
| key-check | `raw/models` | 1 | none (HTTP 200; `subq-snap-preview` present) | 0 | none — see seals | 1 → 1 | [] |
| smoke Banking77 | `raw/smoke/banking77` | 3/3 | {} | 1,860 | `0ccc22c1430cc1d4f6af3a5403bea6a52b56c7109dd3ad8e45ddec9f9c7a038b` | 4 → 4 | [] |
| smoke CLINC150 | `raw/smoke/clinc150` | 3/3 | {} | 2,644 | `84ec44183f546fea6908abeb9c4c791a16956021effa73d549852c73c1d93d28` | 4 → 4 | [] |
| drift-start Banking77 | `raw/drift/start/banking77` | 50/50 | {} | 31,024 | `2502a0b622897260a07155fb0fed511dd3b3961950262e1858c64b7ab6b9c0af` | 4 → 4 | [] |
| drift-start CLINC150 | `raw/drift/start/clinc150` | 50/50 | {} | 44,191 | `5ea6d88c366305a3223af8cd8d573f7d0f72c40f28d85b301a0d984ec19985d1` | 4 → 4 | [] |
| pass1 Banking77 | `raw/pass1/banking77` | 3080/3080 | `{"0": 1}` | 1,910,798 | `a191c4ee5e48c711c506e4d159eb4b7c4a7867d0f7b2cc2e0c7ffafa5ac6412e` | 4 → 4 | [] |
| p2 Banking77 | `raw/order-probe/banking77` | 650/650 | {} | 403,376 | `b51a20d0d961d1ddd215f6eb2a63d6b0acf307e862241d2e376cfbb079ea0890` | 4 → 4 | [] |
| pass1 CLINC150 | `raw/pass1/clinc150` | 5500/5500 | `{"0": 4}` | 4,853,211 | `5662c296f6ad3adc91866d8ded1f287a17525f7211f695b0898f2ae9ad167855` | 4 → 4 | [] |
| pass2 Banking77 | `raw/pass2/banking77` | 3080/3080 | {} | 1,911,416 | `4447de2dcab9395ff00d219b333fb1a27a0060934853f312c41136ae36589028` | 4 → 4 | [] |
| pass2 CLINC150 | `raw/pass2/clinc150` | 5500/5500 | `{"0": 1}` | 4,855,854 | `341da5925664055f1026d530e1d3fa98268353dd9c7fab258862252b959ea4f5` | 4 → 4 | [] |
| pass3 Banking77 | `raw/pass3/banking77` | 3080/3080 | `{"0": 4}` | 1,908,956 | `cb81d2dff129561ae6590c91ad4f49abf64cc6b19f8670898ce65e08d50befcc` | 4 → 4 | [] |
| pass3 CLINC150 | `raw/pass3/clinc150` | 5500/5500 | {} | 4,856,737 | `70b39315b1d04025d75a329378d991a3c3cf1e77e3e241bd5c642537bf6d37cd` | 4 → 4 | [] |
| drift-end Banking77 | `raw/drift/end/banking77` | 50/50 | {} | 31,024 | `09703a4e1cc511cd5436ee73340ce481dc56d5ff015e81c89b7aceec9cec3d31` | 4 → 4 | [] |
| drift-end CLINC150 | `raw/drift/end/clinc150` | 50/50 | {} | 44,191 | `dfd27b3660472ec9d07d9d229551ec03c08e1c38d4d3de5c5d2a03ec912d13e8` | 4 → 4 | [] |

Key-check workers are 1 because `run.py` hardcodes `workers_initial` and `workers_current` to 1 for that step. I still did not pass `--workers`. Every other step recorded 4 → 4. No circuit-breaker trip on any step. No 401, 402, or 403. No step set `stop_reason`. Every manifest has `"completed": true`.

`body.model` on status-200 records is only `subq-snap-preview`. The ten status-0 records have no `body.model`, which is why those counts are 3,079 / 5,496 / 5,499 / 3,076 on the four affected steps.

## The ten status-0 records

All ten are `URLError(TimeoutError(60, 'Operation timed out'))`, attempt 1, retries `[]`. Errno 60 is `ETIMEDOUT`. Elapsed time on each is about 18.06 s, so this is not the harness 60 s Banking77 timeout and not the 120 s CLINC full-pass timeout. Protocol §8.3: network errors are not retried. The steps still completed their planned n. I did not delete or replay them.

| File | id | tag | ms |
|---|---|---|---:|
| `raw/pass1/banking77/responses.jsonl` | b77-2792 | pass1 | 18062.4 |
| `raw/pass1/clinc150/responses.jsonl` | c150-0510 | pass1 | 18071.6 |
| `raw/pass1/clinc150/responses.jsonl` | c150-0511 | pass1 | 18061.0 |
| `raw/pass1/clinc150/responses.jsonl` | c150-0512 | pass1 | 18056.0 |
| `raw/pass1/clinc150/responses.jsonl` | c150-0513 | pass1 | 18060.8 |
| `raw/pass2/clinc150/responses.jsonl` | c150-4279 | pass2 | 18065.6 |
| `raw/pass3/banking77/responses.jsonl` | b77-0364 | pass3 | 18069.1 |
| `raw/pass3/banking77/responses.jsonl` | b77-0365 | pass3 | 18073.3 |
| `raw/pass3/banking77/responses.jsonl` | b77-0366 | pass3 | 18069.8 |
| `raw/pass3/banking77/responses.jsonl` | b77-0367 | pass3 | 18068.6 |

Two clusters of four consecutive ids, plus two singles.

## Totals

- Decision records written (steps 2–12): **26,596**. Plus one `GET /v1/models`.
- Status 200 decision records: 26,586. Status 0: 10. No other non-200 status.
- Input tokens, sum of `input_tokens_this_step` across the 13 decision steps: **20,855,282**. The last manifest's `cumulative_input_tokens` is the same number. Max per-request input tokens seen: 906.
- Listed-price cost from that sum at $0.05 per 1M input tokens: **$1.0428**. I did not read the console. Captain's pre-run balance read of $10 was not re-checked by me.
- Cap: 60,000,000. Actual tokens are 34.8% of the cap. Projection before step 4 was 20,879,478.
- Wall clock from the first Banking77 drift-start call to the last CLINC150 drift-end record: **2028.525 s** (33 min 48.525 s). First call start `2026-10-12T22:08:48.063613-05:00` (record `ts` minus that record's `ms`). Last record `2026-10-12T22:42:36.588368-05:00`. Key-check itself started `2026-10-12T22:07:45.363605-05:00`.
- Host on every manifest: `Sokpyeons-MacBook-Pro-3.local`. Location: `Dallas, TX`.

## Seals (§8 step 13)

Thirteen decision directories each have `responses.jsonl`, `responses.sha256`, and `MANIFEST.json` with `"completed": true`. I recomputed SHA-256 of each `responses.jsonl`; each matches both the seal file and `MANIFEST.json` `responses_sha256`.

**Does not have `responses.sha256`:** `raw/models` (key-check). It has `MANIFEST.json` (`"completed": true`) and `response.json`. The harness writes no `responses.jsonl` for that step, so it writes no seal file. I did not add one.

## Docs re-capture (§8 step 14)

New directory `docs-recapture/`. `docs/` was not written. Fetched `2026-10-13T03:44:16Z` (22:44:16 CDT), each URL HTTP 200. Markdown and `llms.txt` are the curl bytes. Launch-post and terms text were extracted with the committed `prep/open13_strip.py` (script/style stripped, tags to newlines, entities unescaped, nonempty stripped lines joined, no added final newline). Compared to the hashes in frozen `DOCS.sha256`:

| File | Result | sha256 |
|---|---|---|
| `decisions-api.md` | MATCH | `65fa1462bbf2bdb05b7fdb2dea76f4509582f37e135934fb5e33314d4a774ea2` |
| `llms.txt` | MATCH | `69f877425ea8ece1125570f024ae8c0be667e74bbb81045f1273f254c5b21528` |
| `models.md` | MATCH | `0a183f9c9e9bf69b731192c71106586cd3e01598bea064c703a2e0bbe0456d6d` |
| `data-retention.md` | MATCH | `27825993c6a9f355b23491880e4cd72958242d68c0b9da6f9a7de6d1ba9ac049` |
| `introducing-subq-snap.html` | MATCH | `25e968e055bc4aae646d20e91d864f011737ab975ef18d70fbbf48865fb4f85d` |
| `introducing-subq-snap.txt` | MATCH | `9d25ea04f812f00565d5fa0d5332dfc84b2519c6c38c94be307fa93f910b0d23` |
| `terms.html` | MATCH | `fadddcae213dbe2677f8e7f550a01098153bb5a83b662c5f3f068cb9f15e6607` |
| `terms.txt` | MATCH | `55abe3756f1733f29a937219d4df88d6eeeb4c3a5458f258058551adc739076b` |

**Not re-fetched:** `docs/CAPTURE.json` (pinned in `DOCS.sha256`). It is the prior capture's own metadata, not a page in §12.4. I did not regenerate it and I did not treat the missing re-fetch as a content diff. No page hash differed, so nothing was "fixed."

## Unusual, disclosed

1. Ten status-0 timeouts, above. Clustered. No retry, per the frozen rule. Steps still reached planned n.
2. Default route during this session was `en0`, which `networksetup -listallhardwareports` names **Wi-Fi** (`inet 192.168.1.89`, status active). Ethernet adapters `en3`–`en5` exist and were not the default route. OPEN-4's resolution says a wired host. I did not change the route, and I am not claiming the timeouts were caused by Wi-Fi.
3. Smoke probabilities came back at 14–20 decimal places. The docs' examples are 1/0 and 2 decimals. Finer than 2 decimals does not open the step-3 window. Noted so nobody reads the smoke as "2 decimal places, as the examples show."
4. `raw/models` has no `responses.sha256`, as above.

## Not claimed

No calibration number, no accuracy number, no probe result, no CLEAR. The raw files are what Bulma re-scores and what Pan gates.
