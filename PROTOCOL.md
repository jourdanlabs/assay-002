# ASSAY Engagement 002: SubQ Snap, pre-registered measurement protocol

> **DRAFT, 2026-10-12. Not frozen. No API calls have been made and the key has not been used.** Every item marked **OPEN** must be resolved or cut, in writing, before the freeze commit (§12).

| | |
|---|---|
| **Subject** | SubQ Snap, model id `subq-snap-preview` (Subquadratic). Decisions API, `POST https://api.subq.ai/v1/systemone`, public preview. Launch post: subq.ai/introducing-subq-snap, dated 2026-10-12. |
| **Auditor** | ASSAY, a JourdanLabs verification practice |
| **Fee** | None. Unsolicited and self-initiated. Run on Captain's free preview tokens (**OPEN-1**). Subquadratic did not ask for this, does not pay for it, and gets no edit and no veto. |
| **Protocol author** | Pan |
| **Frozen** | Not yet. The date, commit and SHA-256 are filled in at freeze (§12). |
| **Sister engagement** | ASSAY-001, TypeSafe Jev (`jev-latest`, which resolved to `jev-1.13.0`), run 2026-09-17 by machine clock |
| **Publication** | Whatever this returns gets published, with every result given the same weight (§16) |

🐦‍⬛ + 🔑

---

## 0. The rule this protocol lives under

None of the numbers below has been measured yet. This document exists so that nobody, including us, can say the method was chosen after the result was known.

- At freeze, three kinds of hash go into `FREEZE.sha256`: the SHA-256 of this file, of the scorer spec (Appendix A, frozen as its own file), and of every pinned input. `FREEZE.sha256` is committed, and its own hash is posted publicly before the first API call (**OPEN-6**: where).
- After freeze, every change is an **amendment**. Each amendment is numbered, dated by machine clock, kept in its own file, states its reason, and is added to `FREEZE.sha256`. An amendment that changes any headline sentence (§7) says so in its first line.
- Output is labeled "frozen" only if the frozen code produced it.
- Every date and time in the receipt comes from git or `MANIFEST.json` (machine clock, with the UTC offset stated). None comes from hand-typed prose.
- ASSAY-002 copies ASSAY-001 wherever Snap's API allows. Every departure is listed in §4, with its consequence.

## 1. What this measures, and what it does not claim

### 1.1 There is no vendor claim to test

On 2026-10-12 I read the launch post, the docs.subq.ai Decisions API page, the Models page and llms.txt. On those pages Subquadratic makes no calibration claim and no type-safety claim. The launch post contains no form of "calibrat".

ASSAY-001's verdicts were tied to TypeSafe's own verbatim claims, and its protocol (§1) calls testing a claim nobody made a strawman. So **ASSAY-002 is a measurement, not a test of a claim.** No sentence in the report says "the claim does not hold."

These are the vendor's words closest to what we measure, quoted verbatim:

| Source | Wording | Use here |
|---|---|---|
| Decisions API page, description line | "Turn text or structured state into typed decisions with probabilities and confidence." | Context only. We measure the probabilities and check the types. |
| Decisions API page | "Set thresholds from your own data." | Context only. Any threshold readout here applies to these two corpora and nothing else. |
| Decisions API page | "Outputs can vary between requests" | This is why we run three passes (§4, F3). |
| Launch post | "process 100K tokens and return a decision in ~1 second" | Not tested. Our requests are short intent queries, not 100K-token inputs. We observe and report latency but never compare it against this figure. |

### 1.2 What is measured

| # | Quantity | Field | Role |
|---|---|---|---|
| M1 | Calibration of the chosen option's probability | `answers.intent.probabilities[answers.intent.choice]` | Headline (§7). Snap gets no pass/fail. |
| M2 | Type errors: ASSAY-001's response-shape checks | `answers.intent.*` | Headline count (§7) |
| M3 | Latency, as observed from our network | client-side ms | Reported, not judged |
| P1 | Pass-to-pass stability over three passes | choice, p | Reported |
| P2 | Option-order sensitivity, paired within the session | choice, p | Reported |
| P3 | Out-of-scope readout (CLINC `oos`) | choice, p, confidence | Reported |
| P4 | Top bin, the 1.00 atom, and the 0.9-floor readout | p | Reported |
| P5 | Drift slice, `model` field, re-hash of the docs | choice, p, `model` | Reported |

### 1.3 Not measured and not claimed

- **Noul and Score questions.** Calibration can change sign with question type: a second-hand field report found Jev's Choice and Score answers overconfident and its Noul answers underconfident. ASSAY-002 runs Choice questions only, so it says nothing about Noul or Score.
- **Long context.** Snap is pitched on long context, but these requests are short. Nothing here says anything about 100K-token or 384K-token inputs.
- **Any other corpus.** Both of our corpora appear in Snap's own launch table (CLINC150+OOS and BANKING77), so treat them as vendor showcase sets. A result here says nothing about corpora the vendor does not report.
- **Accuracy as a quality verdict** (see the contamination caveat in §2). We also neither repeat nor adjudicate the vendor's accuracy figures (CLINC150+OOS 91.5, BANKING77 80.6).
- **Any head-to-head with Jev or any other model** (§7.4). ASSAY-001's Jev numbers appear only as a labeled historical reference (Appendix B).
- **The vendor's benchmark numbers** (Decision Index, Nimble, LCR, RULER, When2Call). They are self-reported and unverified, and we do not touch them.
- **Images, video, security, prompt injection and jailbreaks.** The terms forbid vulnerability probing without written authorization (§10).
- **Fitted recalibration**: temperature, Platt, isotonic, or the CORP decomposition (which fits an isotonic map). The terms forbid using Output to develop a model, and fitting a map to Snap's output might count. This stays out until a lawyer has read the terms (**OPEN-7**).
- **Any relationship between SubQ and TypeSafe.** We note that they share the path `/v1/systemone` and the same request shape, and claim nothing more.
- **TURNSTILE thresholds.** No ASSAY-002 number may set a TURNSTILE threshold unless the TURNSTILE hidden set is disjoint from these corpora and sealed first.
- **The word "first."** Never.

## 2. Corpora: the same files as ASSAY-001, pinned and hashed

The corpora are reused byte-for-byte from `/Users/sokpyeon/projects/assay-001/corpus/`. Every hash below was re-verified with `shasum -a 256 -c CORPUS.sha256` on 2026-10-12, and all passed. These are exactly the files that get hashed and read; nothing else counts as a source.

| Corpus | Split | n | Options | Source (the file actually hashed) | SHA-256 | License |
|---|---|---|---|---|---|---|
| Banking77 (PolyAI) | official test | 3,080 | 77 | GitHub `PolyAI-LDN/task-specific-datasets` @ `57ec275d8078af65b7731c2a98be812d844a6d6b`: `banking_data/test.csv` (columns `text`, `category`) and `categories.json` | test.csv `d12d6e3bc4c3103966ae786dc435913c0c563dfa328f5a3646d0e62cfeeb474d`; categories.json `53261da888122daf2d120d925458631d9619e15d82e56052e7a42e535ce32b63` | CC-BY-4.0 |
| CLINC150 (`clinc_oos`, `plus` config) | official test, including out-of-scope | 5,500 (4,500 in-scope + 1,000 `oos`) | 151 (150 intents + `oos`) | HF `clinc/clinc_oos` @ `155b9c710419136e17307b80d0a13e68cd46b4ec`: `plus/test-00000-of-00001.parquet` (columns `text`, `intent:int`); `intent_names.json` (int to name, 151 names, `oos` at index 42); `README.md` | test.parquet `3e60e45b25bf86543aa5df8ba4fcc674114164e6184f0197690648c2908d0102`; intent_names.json `f790bcd186bae056b54bd014ddd4be127b1dd5eb8353b0e04fbf148e3aab4688`; README.md `e28704a3c04f6b05c286ca2a8891bbf32c69c000dedfc5825d6e1713369b7a89` | CC-BY-3.0 |

- **The HF card is a reference, not the source.** The card `PolyAI/banking77` @ `90d4e2ee5521c04fc1488f065b8b083658768c57` stays in `PINS.txt` for reference only. ASSAY-001's frozen protocol named that card, but the GitHub file is what was actually hashed, and that fact appeared only in an amendment footer. This protocol names the hashed file directly.
- **Item ids follow file row order, exactly as in ASSAY-001:** `b77-0000` to `b77-3079` and `c150-0000` to `c150-5499`. A reader can therefore line up Snap's answer with Jev's sealed answer for the same item.
- **We did not build either corpus.** We will not edit any label.
- **Contamination caveat, stated now.** Both corpora are public and old, and both appear in Snap's launch table. That can inflate accuracy. It does not invalidate the calibration measurement: if the model says 0.9 and is right 90% of the time on this distribution, it is calibrated on this distribution. Accuracy is reported but is never the verdict.

## 3. The request, the answer space, and the calibrated field

### 3.1 The request is ASSAY-001's body byte-for-byte, except for `model`

```
POST https://api.subq.ai/v1/systemone
Authorization: Bearer <key>          (never logged)
Content-Type: application/json
User-Agent: ASSAY-002/1.0

{"state": <query text only>,
 "model": "subq-snap-preview",
 "questions": {"intent": {"type": "choice",
                          "instructions": <the per-corpus string below>,
                          "criteria": {<label>: null, ... every label, in the fixed order}}}}
```

- **Banking77 instructions**, verbatim from ASSAY-001: `Which banking intent does this customer message express? Choose exactly one.`
- **CLINC150 instructions**, verbatim from ASSAY-001: `Which intent does this user request express? Choose exactly one. Choose oos if it matches none of the others.`
- **Zero-shot, one question per request.** Every option description is `null`, which the docs allow ("each option's description may be `null`").
- **Nothing else in the body.** No `images` and no other fields. There are no sampling parameters because the endpoint documents none: no temperature, top_p, seed or logprobs.
- **Client timeout: 60 s.** This is ASSAY-001's value, and the docs' example code also uses 60 s.
- **Published diff against ASSAY-001's request:** only three things change. The host (`api.subq.ai` instead of `api.typesafe.ai`), `model` (`subq-snap-preview` instead of `jev-latest`), and the User-Agent string.

### 3.2 Answer space

- **Banking77:** K = 77 options, all labels in `categories.json` order.
- **CLINC150:** K = 151 options, in `intent_names.json` index order 0 to 150. `oos` (index 42) is an ordinary option.
- **Both are within Snap's limit of 2 to 255 options.** Labels are sent exactly as spelled in the corpus files.
- **The order is frozen and hashed** (`labels/banking77.json`, `labels/clinc150.json`; see §12). Option order is a hidden parameter: ASSAY-001's follow-on probe saw 5.3% of Jev's answers flip when the options were shuffled. Keeping ASSAY-001's order keeps the two engagements comparable.
- **Gold label:** `category` for Banking77, `intent_names[intent]` for CLINC150.

### 3.3 What is read from each response

We read `body.model`, `body.answers.intent.{type, choice, probabilities, confidence}` and `body.usage.{input_tokens, output_tokens}`. On an error, the first 2,000 characters of the body are logged verbatim. (Snap's errors use the shape `{detail: {error_type, message}}`.)

### 3.4 The calibrated field, fixed now (the lesson of ASSAY-001's Amendment 1.1)

- **Gated field:** `p = probabilities[choice]`, the probability Snap gives to the option it chose. `correct = 1` if `choice` equals the gold label, otherwise 0.
- **Not the gated field:** `confidence`. The docs never define it: there is no formula, no range and no statement about calibration. In the docs' Score example, confidence is 0.79 while the top probability is 0.87, so confidence is not simply the maximum probability. It is reported as a secondary field only (§5.6).

## 4. Differences from ASSAY-001

### 4.1 Differences forced by Snap's API or docs

| # | ASSAY-001 (Jev) | ASSAY-002 (Snap) | Consequence |
|---|---|---|---|
| F1 | Host `api.typesafe.ai`, model `jev-latest` | Host `api.subq.ai`, model `subq-snap-preview` | Different subject. Only the host, model and User-Agent change, and that diff is published. |
| F2 | `jev-latest` resolved to `jev-1.13.0` in `body.model` | No pinned version or alias is documented. The docs' example response echoes `subq-snap-preview`, and during preview "Model availability and capabilities may change". | Results are tied to the alias, the run window and the docs hashes. `body.model` is still recorded on every call, and a drift slice brackets the run (P5). A later re-run is a new measurement, not a replication. |
| F3 | One pass | **Three passes per corpus** | The docs say "Outputs can vary between requests" and offer no seed or temperature, so a single pass would hide that variation. The headline rule across the three passes is fixed in §7. Pass 1 is the like-for-like counterpart of ASSAY-001's single pass. The number of calls roughly triples. |
| F4 | Verbatim claims C1–C3, judged pass/fail | No claims | Measurement sentences only (§7) |
| F5 | Retried 429, 529 and network errors, up to 8 tries | Retries 429 and 5xx only, up to 8 tries, with the same backoff | The docs say "Retry `429` and `5xx` with backoff" and never mention 529. Network errors are no longer retried (this is also an ASSAY-001 lesson; see §4.2). Losses on our side lower n and are disclosed, so the run uses a wired, stable host (**OPEN-4**). |
| F6 | Probabilities came back at 2 decimals; sums ranged 0.99–1.0 | Precision is undocumented. The doc examples show 1/0 and 2-decimal values. | The sum tolerance is frozen at 0.02, and the sum check never removes an item from M1 (§5.2), so the tolerance cannot move ECE. The smoke test may trigger one pre-run amendment, of the tolerance only (§8, step 3). |
| F7 | The definition of `confidence` was unpublished | `confidence` is undefined everywhere | Secondary only, as in ASSAY-001's A1.1 |
| F8 | n/a | The default retention policy is "Retain indefinitely". `store: false` is documented only for Chat Completions and Responses, not for Decisions. | SubQ will keep our inputs and its decisions. Our inputs are public, licensed corpus text only (§10). Zero data retention is available org-wide on request (**OPEN-8**). |
| F9 | Jev's tokenizer | Snap's tokenizer differs, and there is no token-count endpoint | ASSAY-001's token counts do not carry over. The cap is set from the smoke test's `usage.input_tokens` (§9). |
| F10 | n/a | No numeric rate limits are published, only the `429` code | One key, a fixed worker count, backoff, and a pre-registered circuit breaker (§8) |
| F11 | n/a | The API returns 402 when credits run out | A 402 stops the run (§8) |
| F12 | `choice` being the argmax was implied by Jev's docs | Snap's docs do not state it | Reported as an observation, not as a violation (§5.3) |

### 4.2 Changes chosen from ASSAY-001's lessons (not forced)

| # | Change | The lesson behind it |
|---|---|---|
| L1 | The scorer spec (Appendix A) is frozen together with the protocol | ASSAY-001's spec was written after the run, with Amendment 2's tolerance already built in, so neither the gate nor the re-scorer could catch the C2 flip |
| L2 | The sum tolerance is fixed before the run. The sum check never drops an item from M1. Counts at both 1e-3 and 0.02 are published. | ASSAY-001's post-run tolerance change flipped C2 from FAIL to PASS (the frozen scorer gives 145 and 368 C2 violations; verified in the committed score files and published as ASSAY-001 Erratum 1 on 2026-10-12), yet the report said the verdicts did not change |
| L3 | The argmax check is its own row from the start | ASSAY-001 moved it out of C2 after the run |
| L4 | MCE is reported over all populated bins and also over bins with n ≥ 50 | ASSAY-001's Banking77 MCE of 0.86 came from a single item in one bin, and its CLINC "n ≥ 50" cut was added after the fact |
| L5 | The option-order probe is pre-registered and paired within the session | The 09-20 probe compared against a sealed run that was days old |
| L6 | Host location, worker count and retry policy are pre-registered and written into `MANIFEST.json`. The latency location is read from the manifest and never hard-coded. | The location was recorded as both Plano and The Woodlands; `score.py` line 115 hard-coded Plano; in-run retries went undisclosed |
| L7 | `run.py` reads the protocol hash from `FREEZE.sha256` at run time | `run.py` line 87 hard-coded it |
| L8 | Controls are re-run after every scorer change, and each control output records the scorer's SHA-256 and the tolerance used | ASSAY-001's controls ran only against the pre-Amendment-2 scorer |
| L9 | The receipt list in §17 matches what ships, and the reliability PNGs are committed | ASSAY-001 shipped no `RERUN.sh` and no `scores.json`, and gitignored `*.png` |
| L10 | Each table row comes from a single scorer | ASSAY-001's verdict table put a frozen-scorer MCE next to an amended ECE |
| L11 | No unexplained files in the receipt | `rescore/rescore_ornith.py`, an unexplained 4-line fragment |
| L12 | Extra metrics are reported: equal-mass ECE, a bootstrap interval, a noise floor, the 1.00 atom, and OOS AUROC. Of these, only the interval enters the headline, and only as a clause. | 0.05 is a convention, ECE is not a proper scoring rule, and the field finding that "0.9 is not one number" |

## 5. Metrics (exact definitions are in Appendix A)

### 5.1 M1: calibration, per corpus and per pass

- **ECE with 10 equal-width bins.** This is the column that stays comparable with ASSAY-001. Bin 0 is [0, 0.1]; bin i is (i/10, (i+1)/10] for i = 1..9. ECE is the sum over populated bins of (n_b / N) · |acc_b − mean_p_b|.
- **MCE**, computed over all populated bins (comparable with ASSAY-001) and over bins with n ≥ 50 (pre-registered here).
- **A per-bin table** giving n, mean p, accuracy and the signed gap (mean p minus accuracy).
- **Equal-mass ECE:** the same formula applied to 10 contiguous slices of the items sorted by p.
- **Multiclass Brier:** the mean over items of the sum over all K options of (p_k − y_k)².
- **A bootstrap 95% interval for ECE:** 2,000 resamples of the items, with a fixed seed.
- **The noise floor:** the ECE that a perfectly calibrated model with these same p values would show by chance. It comes from 2,000 simulations with a fixed seed, and we report the mean and the 95th percentile.
- **Direction.** "Over" means every bin with n ≥ 50 has mean p ≥ accuracy. "Under" means every such bin has mean p ≤ accuracy. Anything else is "mixed". We also report the overall signed gap, mean p minus accuracy.
- **Reliability diagram:** bin mean p plotted against bin accuracy, with the diagonal drawn and n written on each bin. There is one PNG per corpus per pass, and all are committed.
- **Accuracy:** mean(correct). It is reported with the contamination caveat and is never the headline.

### 5.2 M2: type errors (ASSAY-001's checks, applied to every status-200 record)

| Check | Documented by Snap? |
|---|---|
| a. `answers.intent` is an object | Yes (answer keys match the question names) |
| b. `type` == `"choice"` | Yes |
| c. `choice` is one of the options | Yes |
| d. `probabilities` is an object | Yes |
| e. Its keys equal the option set exactly | Yes ("a probability for every option") |
| f. Every value is a number in [0, 1], and is neither NaN nor a boolean | Yes (each value is a probability) |
| g. abs(sum − 1) ≤ 0.02 | **No.** The docs do not say the probabilities sum to 1. |
| h. `confidence` is a number in [0, 1] | **No.** The docs give no range. |

- **A type error** is a status-200 record that fails any of checks a–h. This is ASSAY-001's check, kept for comparability. The count is split two ways: **documented** errors (failing any of a–f) and **undocumented-only** errors (passing a–f but failing g or h).
- **Also published:** the minimum and maximum probability sum, and how many sums differ from 1 by more than 1e-3.
- **The calibration set** is every status-200 record whose p can be read. That means `answers.intent` is an object, `choice` is one of the options, `probabilities` is an object containing `choice`, and that value is a number in [0, 1]. Failing check b, e, g or h does not remove a record from M1. No type check ever silently drops an item from the calibration score.
- **Non-200 responses are not type errors.** They are counted by status code and disclosed.

### 5.3 Contract observation: is `choice` the argmax?

We count calibration records where p[choice] < max(p) − 1e-9. Snap does not document that `choice` is the argmax, so this row is an observation, not a violation. (For Jev there were 3 such records out of 8,576, all within 0.01 of a tie.)

### 5.4 M3: latency (an observation)

We report the median, p95 and p99 (numpy percentile, linear) of client-side milliseconds, measured with `time.perf_counter` around `urlopen`. Only status-200 records with attempt == 1 are counted. The figures include the public internet path from the host location recorded in `MANIFEST.json`. Latency is reported per corpus and per pass, together with the worker count, and is never compared with the vendor's 100K-token latency claim.

### 5.5 Bookkeeping

We report the number of records, non-200 counts by status code, the number scored, the histogram of attempts, the distinct `body.model` values with their counts, and the sum of `usage.input_tokens`.

### 5.6 Secondary: Snap's `confidence` field (reported, never gated)

We report accuracy by decile of `confidence` (10 slices of the items sorted by confidence), a check that accuracy never decreases from decile to decile, ECE on `confidence` using the same 10 bins, and the share of answers with confidence exactly 1.00.

## 6. Pre-registered probes

Each probe below is cheap (it needs no new corpus and at most 650 extra calls) and is fully defined here. Probes that did not meet both conditions are listed as excluded in §6.6.

### 6.1 P1: pass-to-pass stability (uses the three passes; no extra calls)

For each corpus and each pair of passes (1–2, 1–3, 2–3) we report three things:

- the flip rate: the share of items whose `choice` differs;
- the distribution of abs(Δp) on stable items: its median, and the share above 0.05;
- the count of items whose p crosses 0.9: above 0.9 in one pass and at or below 0.9 in the other.

ECE per pass is already part of M1. For reference, a second-hand field report found that about 3% of Jev's answers changed across 5 runs of 300 items.

### 6.2 P2: option-order sensitivity, paired within the session (650 calls)

- **Slice:** the first 300 Banking77 test items in file order, with no selection.
- **Shuffles:** built exactly the way ASSAY-001's `harness/permute.py` built them. `rng = random.Random(20260920)`; then, for each of the 300 items in file order, `shuffled = labels[:]; rng.shuffle(shuffled)`. These are the same 300 orderings that were sent to Jev on 2026-09-20.
  - A local pre-check on 2026-10-12, using the system Python 3.9.6 with no API calls, reproduced all 300 against the `order_first5` field of the "shuffled" records in `assay-001/raw/permutation-2026-09-20/responses.jsonl`: 300 of 300 matched.
  - At freeze, the 300 orderings are written to `labels/b77-permutations-300.json`, hashed, and checked again. All 300 must match, or the freeze stops.
- **Calls:** for each item i, one worker sends **O_i** (the canonical order) and then **S_i** (the shuffled order), back to back. After that, the first 50 items are asked again in the canonical order (**O2_i**).
- **Primary metrics:**
  - the flip rate of S against O (n = 300) and of O2 against O (n = 50);
  - the accuracy of flipped items and of stable items;
  - the share of flips where neither answer has p > 0.9, also reported under ASSAY-001's definition (p < 0.9 on both sides);
  - the share of stable items with abs(Δp) > 0.05.
- **Secondary metrics,** matching the 09-20 structure: S against Banking77 pass 1, and O2 against pass 1.
- **Jev reference** (09-20; historical, not a head-to-head): 16 of 300 answers flipped (5.3%), against 0 of 50 in the same order. All 16 flips had p < 0.9 on both sides. abs(Δp) exceeded 0.05 on 28.5% of stable items, against 12% in the control.

### 6.3 P3: out-of-scope readout (CLINC150; no extra calls)

For each pass, over the 1,000 `oos` items and the 4,500 in-scope items, we report:

- accuracy on oos and accuracy in-scope;
- mean p on oos against in-scope;
- mean `confidence` on oos against in-scope;
- the share of oos items answered wrongly with p > 0.9;
- the AUROC of p for telling in-scope items from oos items, with ties counted as half.

Jev reference: oos accuracy was 0.723, mean chosen-option p on oos was 0.7903, and mean confidence was 0.7799 on oos against 0.9176 in-scope.

### 6.4 P4: the top bin, the 1.00 atom, and the 0.9 floor (no extra calls)

For each corpus and each pass:

- For three groups (p > 0.9, which is the top bin; p ≥ 0.9; and p exactly 1.00 after rounding to 6 decimals), we report the share of traffic, the accuracy, and a 95% Wilson interval.
- We give the floor readout in the same form as Jev's, using the rule "ship if p > 0.9": the share of shipped answers that are right, the number of wrong answers shipped (with and without the floor), and the share refused. Jev Banking77 reference: right answers went from 79.8% to 92.7%, wrong answers shipped went from 623 to 155, and 31% were refused.

### 6.5 P5: drift and version control (200 calls)

- **Drift slice:** the first 50 Banking77 items and the first 50 CLINC150 items, in canonical order. Each is asked once at the start of the run (before pass 1) and once at the end (after pass 3). We report the flip rate between start and end and the distribution of abs(Δp).
- **Model values:** the distinct `body.model` values across every response, with counts.
- **Docs:** the docs pages are captured and hashed again after the run. Any change from the freeze hashes is disclosed, with a diff.

### 6.6 Probes considered and excluded

| Probe | Why it is not in ASSAY-002 |
|---|---|
| Noul and Score arms (BoolQ, yelp stars) | They need new corpora, pinned and hashed, and that is not cheap to define well now. Candidate for ASSAY-003 or for addition before freeze (**OPEN-10**). |
| A corpus that is not in Snap's launch table (LEDGAR, Web of Science, DAIR Emotion, Russian XNLI) | Same reason: none is pinned. This is the honest test of whether a showcase result generalizes, so it is the first candidate for ASSAY-003 (**OPEN-10**). |
| A context-length axis | Exploratory, the filler design is not pinned, and each call costs far more. |
| An option-count sweep | Not needed for comparability. Option count alone also did not explain Jev's split: CLINC with 151 options was calibrated, Banking77 with 77 was not. |
| A permutation pass over the full corpus | Roughly doubles the Banking77 calls, and P2 already gives the like-for-like rate (**OPEN-11**). |
| A paired Jev arm in the same window | Needs another vendor's API and key, which is out of scope for an engagement on Snap (**OPEN-9**). |
| Fitted temperature, Platt, isotonic or CORP | Blocked by the terms (§10) until a lawyer has read them. |
| smoothECE | No implementation is pinned, so two scorers working from a spec could not reproduce it to ±0.001. |
| Injection or adversarial corpora | The terms forbid vulnerability probing without written authorization. |

## 7. Headline decision rules (fixed before any call)

The score code fills these sentences in mechanically from the frozen rules. Nobody writes the headline by hand.

### 7.1 The calibration sentence (one per corpus)

Let E1, E2 and E3 be the 10-bin ECE of passes 1, 2 and 3 on a corpus. The line is 0.05, the same one ASSAY-001 used. Values are printed to 4 decimals.

| Case | Sentence |
|---|---|
| max(E) ≤ 0.05 | "On ⟨corpus⟩, Snap's chosen-option probabilities measured ECE ⟨E1⟩ (pass 1; ⟨min⟩–⟨max⟩ over three passes), inside the 0.05 line ASSAY-001 used." |
| min(E) > 0.05 | "On ⟨corpus⟩, Snap's chosen-option probabilities measured ECE ⟨E1⟩ (pass 1; ⟨min⟩–⟨max⟩ over three passes), outside the 0.05 line ASSAY-001 used, ⟨direction⟩." |
| Otherwise | "On ⟨corpus⟩, Snap's chosen-option probabilities measured ECE ⟨min⟩–⟨max⟩ over three passes, on both sides of the 0.05 line ASSAY-001 used." |

- **⟨direction⟩** comes from pass 1:
  - "over" becomes "overconfident in every bin with at least 50 items";
  - "under" becomes "underconfident in every bin with at least 50 items";
  - "mixed" becomes "overconfident in some bins and underconfident in others".

  If pass 2 or pass 3 gives a different direction, append "; the direction was not the same in every pass".
- **Interval clause.** If 0.05 falls inside the pass-1 bootstrap 95% interval, append "(pass-1 95% interval ⟨lo⟩–⟨hi⟩ includes 0.05)".
- **Incomplete passes.** If a pass did not complete (§8), the sentence uses only the completed passes and says "⟨k⟩ of 3 passes completed". The cases in the table are then evaluated over the completed passes.

### 7.2 The type-error sentence

- **If V = 0:** "Across ⟨N⟩ responses there were zero type errors under the checks ASSAY-001 used."
- **If V > 0:** "Across ⟨N⟩ responses, ⟨V⟩ failed the checks ASSAY-001 used: ⟨D⟩ against Snap's documented response shape and ⟨U⟩ only against checks Snap does not document (probability sum within 0.02, confidence in [0, 1])."

N is the number of status-200 responses across both corpora and all three passes.

### 7.3 Rules for how the sentences travel

- **They travel together.** Both corpus sentences and the type-error sentence always appear together, followed by the limit clause.
- **Accuracy always carries the caveat.** No accuracy number appears without it: "Both corpora are public and old and both appear in Snap's own launch table, so accuracy is reported, not judged."
- **The limit clause:** "A result applies to the artifacts and criteria examined: `subq-snap-preview` as served between ⟨first call⟩ and ⟨last call⟩ (response `model` values: ⟨values⟩), Choice questions with null option descriptions in ASSAY-001's option order, these two corpora, and the docs pages hashed at freeze. It is not a statement about Snap on any other task, question type, corpus, context length or day."
- **Probe sentences are pre-shaped too.** Examples: "With the 77 options shuffled, Snap changed its answer on ⟨x⟩ of 300 Banking77 items; re-asked in the original order, on ⟨y⟩ of 50." "Between passes, Snap changed its answer on ⟨r⟩ of Banking77 items and ⟨s⟩ of CLINC150 items."

### 7.4 Comparison scope

We take option (a) from the field lessons: **no model comparison.** Jev's ASSAY-001 numbers appear only in a separate table, and each one is labeled "historical reference: Jev, `jev-latest` → `jev-1.13.0`, single pass, 2026-09-17. Different model, date and version. Not a head-to-head."

The new metrics (equal-mass ECE, the interval, the noise floor, AUROC and the 1.00 atom) are computed for Jev by the ASSAY-002 scorer from ASSAY-001's sealed files, so the reference column comes from the same code. No call is made to Jev's API.

### 7.5 What may not be said

- "Snap is calibrated" or "Snap is not calibrated", unqualified
- "The claim does not hold" (there is no claim)
- "First"
- That Snap is better or worse than Jev or any other model
- Vendor numbers cited as if they were independent
- Accuracy presented as a quality verdict
- Anything about Noul, Score, long context, images, other corpora or other days
- Any number from a pass or probe that did not run

## 8. Run sequence, pacing and retries

### 8.1 Sequence

| Step | What happens | Calls |
|---|---|---|
| 0 | Freeze (§12). No API calls. | 0 |
| 1 | Key check: one `GET https://api.subq.ai/v1/models`. Log the model ids, never the key. Stop if `subq-snap-preview` is absent. | 1 (not a decision call) |
| 2 | Smoke test: the first 3 items of each corpus, in canonical order, written to `raw/smoke/`. Excluded from all scoring and disclosed. It checks connectivity, the response shape, probability precision, and `usage.input_tokens` per request. | 6 |
| 3 | Pre-run amendment window. Only two things may change, each by a numbered amendment citing the smoke evidence: (i) the sum tolerance, if the smoke test shows probability precision coarser than 2 decimals; (ii) the cap projection (§9). Nothing else may change. The window closes at the first call of step 4. | 0 |
| 4 | Drift slice, start (P5) | 100 |
| 5 | Banking77 pass 1 | 3,080 |
| 6 | P2 option-order probe | 650 |
| 7 | CLINC150 pass 1 | 5,500 |
| 8 | Banking77 pass 2 | 3,080 |
| 9 | CLINC150 pass 2 | 5,500 |
| 10 | Banking77 pass 3 | 3,080 |
| 11 | CLINC150 pass 3 | 5,500 |
| 12 | Drift slice, end (P5) | 100 |
| 13 | Seal: each `responses.jsonl` is hashed when its step ends, and `MANIFEST.json` is written | 0 |
| 14 | Re-capture the docs pages and hash them again | 0 |
| | **Total decision calls (steps 2–12)** | **26,596** |

- **One window.** Steps 4–12 run as a single session. If any step cannot start within 24 hours of the first call of step 4, the run is declared broken and disclosed, and any re-run needs an amendment.
- **The run window itself** is **OPEN-5**; Captain picks it.

### 8.2 Pacing

- **Keys:** one API key, never parallel keys.
- **Workers:** 4 (proposed; **OPEN-5**). Four is `run.py`'s default. ASSAY-001's MANIFESTs do not record how many workers it actually used, so this time the count goes into `MANIFEST.json`. In P2, a single worker sends each O/S pair back to back.
- **Circuit breaker:** if at least 20 of the last 100 completed requests needed a 429 retry, the runner pauses for 60 s and halves the worker count (to a minimum of 1) for the rest of the run. Each time this happens it is logged, with its time, in `MANIFEST.json`.

### 8.3 Retries and stops

| Response | Action |
|---|---|
| 429, or any 5xx (including 503) | Retry, up to 8 attempts in all. The delay starts at 1 s and doubles, capped at 30 s. If a `Retry-After` header is present, wait whichever is longer, the header or the delay. |
| 400, 422 | No retry. Counted and disclosed. (The docs say of these: "a retry won't change it.") |
| 401, 402, 403 | No retry. **The run stops.** Disclosed. The run resumes only by amendment. |
| Network error or timeout (status 0) | No retry. Counted and disclosed as a failure on our side. |

Every record logs `attempt` and the status of each earlier attempt. Latency counts only records with attempt == 1.

### 8.4 What each record holds

`{"id", "label", "tag" (pass1/pass2/pass3/O/S/O2/drift-start/drift-end/smoke), "request" (the body only, never the headers), "response": {"status", "ms", "attempt", "retries": [statuses], "body" | "error" (first 2,000 chars)}, "ts"}`

This is ASSAY-001's record shape with `tag` and `retries` added, so `controls.py` and the scorers keep working.

For each step, `MANIFEST.json` holds:

- the corpus, the step or tag, n, and the label count;
- the SHA-256 of the label order;
- the model requested and the exact instruction string;
- the worker count and any circuit-breaker trips;
- the host and its location;
- the start and finish times (machine clock, with offset);
- the protocol SHA-256 as read from `FREEZE.sha256`;
- the full text of `CORPUS.sha256` and `DOCS.sha256`;
- non-200 counts by status code and the histogram of attempts;
- the distinct `body.model` values;
- the cumulative input tokens.

## 9. Compute and cost cap

- **Price** (from the Models page and the launch post): $0.05 per 1M input tokens. Output is free ("output_tokens is always 0"). The account needs prepaid credits; without them the API returns 402.
- **Planned decision calls:** 26,596 (Banking77 9,993; CLINC150 16,603), plus one `GET /v1/models`.
- **A scale reference only.** I summed the input tokens in ASSAY-001's sealed responses on 2026-10-12:
  - Banking77 pass: Jev's tokenizer counted 3,162,010 input tokens (median 1,025 per request, range 1,016–1,092).
  - CLINC150 pass: 7,903,898 input tokens over 5,496 responses (median 1,438, range 1,430–1,461).
  - If Snap counted tokens the same way, the plan would come to about 34–35M input tokens, roughly USD 1.71–1.76 at Snap's listed price. **But Snap's tokenizer is not Jev's.** The real figure comes from the smoke test.
- **Proposed cap (OPEN-2): 60,000,000 input tokens, which is USD 3.00 at the listed price.**
- **Rule 1, before step 4.** The projection is the sum, over the two corpora, of the largest smoke-test `usage.input_tokens` for that corpus multiplied by the planned calls for that corpus. If the projection exceeds 80% of the cap, step 4 does not start. Before any main-run call, either the cap is raised or arms are cut, by amendment.
- **Rule 2, during the run.** The runner keeps a running total of `usage.input_tokens`. It will not send a request that could push the total past the cap, judging by the largest per-request count seen so far. A stop at the cap is disclosed, and the pass is labeled incomplete.
- **Reported cost** is the sum of `usage.input_tokens` times the listed price, computed by code. If Captain reads the billed figure in the console, it goes beside this one (Pan does not sign in). The docs do not say whether requests rejected with 429 are billed.

## 10. Data handling and terms

- **Inputs.** Only the query texts from the two public corpora (CC-BY-4.0 and CC-BY-3.0), plus ASSAY-001's instruction strings and label names. No special-category data. No personal data of ours, or of anyone's beyond what those public corpora already contain. No images. No other text.
- **SubQ's retention.** The default org policy is "Retain indefinitely", and the data-retention page says SubQ always records model, token counts, timing and metadata. `store: false` is documented only for Chat Completions and Responses, not for Decisions. Zero data retention applies org-wide and is requested from SubQ through the data-retention page. As a result, SubQ will keep these public texts and Snap's answers, which is acceptable for public corpus text. Whether to request zero retention anyway is **OPEN-8**; the answer does not change the measurement.
- **Terms** (subq.ai/terms, effective 2026-10-12; read by keyword search and table extraction only, not top to bottom):
  - **No training, fine-tuning or distilling on Output, and no otherwise developing any ML model from it.** So this engagement fits no temperature, Platt, isotonic or CORP map. A fitted temperature may be reported at most as a diagnostic, and only after a lawyer's read (**OPEN-7**). Snap's output is never used as training data or as labels for anything.
  - **No vulnerability probing without written testing authorization.** So there are no injection, jailbreak or adversarial corpora.
  - **No circumventing rate limits or protective measures, and no programmatic extraction in violation of the rate limits or docs.** So we use one key, follow the docs' own retry guidance, back off, use the circuit breaker, and never use parallel keys.
  - **Benchmark publication.** The keyword read found no clause about publishing benchmarks, but it was not a full read. The usage policy, the privacy policy and the data-retention terms have not been read (**OPEN-7**).
- **The key.** It is read from `$SUBQ_API_KEY` or from `~/.config/subq/api_key`. That file is written by `pan-cc/tools/subq-key.zsh`, which takes the key at a hidden prompt and saves it with mode 600. The key is never printed, logged, committed, written into a receipt or pasted into a chat. Request logs hold only the body, never the headers.
- **Labels.** Only human-labeled corpora. Snap, Jev or any other LLM is never used as the oracle.

## 11. Roles

| Role | Who | Notes |
|---|---|---|
| Protocol | Pan (Claude) | This document |
| Harness edits and the run | Proposed: Pan (Claude), on Captain's machine with Captain's key in the environment (**OPEN-3**) | The same arrangement as ASSAY-001's A1.2, but written in from the start this time rather than added by amendment. No model anywhere in the scorer. |
| Key holder | Captain | The key is stored with `tools/subq-key.zsh` and never appears in a chat |
| Blind re-scorer | Someone on a non-Claude base model, and not Ornith (**OPEN-3**) | Writes their own scorer from the frozen spec in Appendix A, blind to Pan's numbers, working only from the sealed raw files. ASSAY-001's precedent was Tifa on Cursor/Grok. |
| Third cross-check | Tifa's ASSAY-001 `rescore.py` (`477d86a77f1a4d177fc1198afaed2be29e00452b289c12d2f965ac080f58496e`, re-hashed 2026-10-12), run by Pan | Used only on fields where its rules match Appendix A. It drops records that fail the sum tolerance from calibration and ASSAY-002 does not, so the two agree only when there are no sum failures. Any difference is shown, not hidden. |
| Gate | Pan | Validates from the files (§15) |
| Call | Captain | Decides on the freeze post and on publication |

Builder ≠ validator: Pan's numbers never publish on their own.

## 12. Freeze procedure (before the key is used)

The repo is `/Users/sokpyeon/projects/assay-002` (proposed; **OPEN-12**).

1. **Corpora.** Copy `corpus/`, `CORPUS.sha256` and `PINS.txt` unchanged from assay-001. Run `shasum -a 256 -c CORPUS.sha256`; every line must report OK. Commit the output.
2. **Option lists.** Write `labels/banking77.json` (in `categories.json` order) and `labels/clinc150.json` (in index order 0..150). These are the exact option lists that will be sent.
3. **Permutations.** Write `labels/b77-permutations-300.json` using the construction in §6.2. Check every permutation against the 09-20 `order_first5` values. All 300 must match.
4. **Docs.** Re-capture the docs into `docs/` with the UTC capture time: the Decisions API page (as markdown), llms.txt, the Models page, the data-retention page, the launch post text and the terms text. Write `DOCS.sha256`.
   - Compare against this session's capture from 2026-10-12T23:58:07Z, re-hashed here: `decisions-api.md` `65fa1462bbf2bdb05b7fdb2dea76f4509582f37e135934fb5e33314d4a774ea2`; `llms.txt` `69f877425ea8ece1125570f024ae8c0be667e74bbb81045f1273f254c5b21528`; launch post text `1583ec9cfeb9c0b984daf6fd87f94400ff6dddb932808df612119952d3714c6a`.
   - The copies go into the repo because the scratchpad is not durable.
   - Any difference is disclosed in the protocol before freeze.
5. **Scorer spec.** Write `SPEC-FOR-INDEPENDENT-SCORER.md` from Appendix A, verbatim.
6. **Harness edits** (starting from a copy of assay-001's harness):
   - **`run.py`:** the `API` and `MODEL` constants; the key loader; the User-Agent; reading the protocol hash from `FREEZE.sha256`; the retry table in §8.3; `tag` and `retries` in each record; the worker count and circuit breaker in the manifest; the cap meter from §9; and the stops on 401, 402 and 403.
   - **`score.py`:** the Appendix A rules, and reading the location from the manifest (removing the hard-coded "Plano, TX").
   - **New `pairs.py`** for P1, P2 and P5.
   - **`permute.py`:** move its logic into the P2 step so it no longer reads the sealed Jev file.
7. **Controls.** Run `controls.py` against the final scorer (§14). The scorer must go red where it should and green where it should. Commit the control outputs, with the scorer's SHA-256 and the tolerance recorded inside them.
8. **Freeze file.** Write `FREEZE.sha256` with the SHA-256 of `PROTOCOL.md`, `SPEC-FOR-INDEPENDENT-SCORER.md`, `CORPUS.sha256`, `PINS.txt`, `DOCS.sha256`, every file in `labels/` and every file in `harness/`.
9. **Commit** with the message "freeze: zero API calls made". Record the commit hash and the machine time.
10. **Post the hash.** With Captain's OK, post the SHA-256 of `FREEZE.sha256` publicly (**OPEN-6**), and keep the post's URL and timestamp in the receipt. ASSAY-001's protocol said its hash was posted before the first call, but that was never verified, so this time the proof is kept.
11. **Only then** is the key loaded and step 1 of §8 run.

## 13. Amendments

- **File:** `AMENDMENT-<n>.md`, numbered from 1. Each amendment gets its own entry in `FREEZE.sha256`.
- **Header:** the number; the machine-clock time; whether it comes before or after the first main-run call; the reason; and the exact text changed.
- **First line, when it applies:** "This amendment changes the headline sentence for ⟨corpus/metric⟩ from ⟨A⟩ to ⟨B⟩."
- **After the run,** both outputs are committed: one under the frozen rule, produced by the frozen code, and one under the amendment. Each is labeled with the code that produced it.
- **Unexplained departures fail the gate.** Any departure the receipt shows that no amendment explains is a gate failure (§15).

## 14. Positive controls (the scorer must be able to fail)

The controls run before Snap is scored, and again after every scorer change. They use synthetic answers in the exact record shape, covering every item of each corpus, with seed 1, built with `run.py`'s request builder (as ASSAY-001's `controls.py` does).

| Control | Expected | ASSAY-001 result |
|---|---|---|
| Uniform-random (p = 1/K on every option) | ECE ≈ 0; accuracy ≈ 1/K | ECE 0.001; accuracy 0.014 / 0.0056 |
| Overconfident (a random choice at p = 1.0) | ECE ≈ 1 − 1/K | 0.986 / 0.9944 |
| Perfect oracle | ECE 0; accuracy 1.0 | 0.0 / 1.0 |
| Broken schema | Every injected break is counted, exactly | 29 / 59 caught |
| Rounded sums (new) | Oracle-like answers rounded so some sums are 0.99. They are counted at 1e-3 but not at 0.02, and the calibration n does not change. | n/a |
| Shuffle-invariance (new to the frozen set; Tifa ran it for ASSAY-001) | Identical output after the record order is shuffled | Passed |
| Pairs (new) | `pairs.py` run on a file against itself gives 0 flips; run against a copy with exactly F choices changed, it gives F | n/a |
| Seed determinism (new) | Two runs give the same bootstrap interval and the same noise floor | n/a |

If any control misses, nothing is scored and nothing is published.

## 15. Independent re-score and the gate

- **The re-scorer's packet** contains the sealed `responses.jsonl` files and their seals, the label files, and the frozen spec. No Pan code and no Pan numbers.
- **The re-scorer runs their own positive controls.**
- **Pan's gate,** worked from the files:
  - re-hash the corpus, freeze, docs and run seals;
  - re-run the re-scorer's code herself rather than trusting their JSON;
  - build a Δ table field by field, for each corpus, pass and probe;
  - check that every float reported to 4 decimals agrees within ±0.001, latency within ±0.1 ms, and every count exactly;
  - confirm the controls pass under the final scorer;
  - confirm the manifests against §8.4;
  - confirm that every file in the receipt is accounted for.
- **On a mismatch:** work out from the files which scorer is wrong, fix it, re-run the controls and gate again. Nothing is published while there is a mismatch.
- **Captain calls.**

## 16. Publication rule

- **Publish whatever we find, at equal weight:** both corpora, every pass and every probe, with good results and bad ones given the same prominence.
- **An aborted or incomplete run is published too,** described as what it is, with its raw files and the reason it stopped.
- **Raw requests and responses are published with the report,** subject to the legal read (**OPEN-7**).
- **Subquadratic gets no edit and no veto.** They are invited to reproduce the work.
- **Venue:** **OPEN-6**.
- **Wording:** never "first". Vendor numbers are never cited as if they were independent.

## 17. Receipt (what ships; this list must match the repo)

**Protocol and freeze files**
- `PROTOCOL.md`
- `AMENDMENT-*.md`
- `FREEZE.sha256`
- `CORPUS.sha256`
- `PINS.txt`
- `DOCS.sha256` and `docs/`
- `SPEC-FOR-INDEPENDENT-SCORER.md`

**Inputs and code**
- `labels/`
- `corpus/`
- `harness/` (`run.py`, `score.py`, `pairs.py`, `controls.py`)
- `controls/`, with outputs

**Raw data**
- `raw/models/` (the key-check response)
- `raw/smoke/`
- `raw/pass{1,2,3}/<corpus>/{responses.jsonl, responses.sha256, MANIFEST.json}`
- `raw/order-probe/`
- `raw/drift/{start,end}/`

**Scores and reports**
- `scores/`: JSON per corpus per pass and per probe, each labeled with the scorer that produced it; reliability PNGs committed
- `scores/jev-reference/`: the ASSAY-002 scorer run on ASSAY-001's sealed files
- `rescore-<name>/`
- `REPORT.md`
- `GATE.md`
- `README.md`, with a re-run block

Every finding cites item ids. Every file in the repo is explained.

## 18. OPEN items (each must be resolved or cut before freeze)

1. **OPEN-1. Free preview tokens.** None of the pages I read gives the balance or where it comes from. The docs describe prepaid credits and a 402, and no free tier. A field note mentions "100M free tokens" as vendor-stated, but no page I captured says so. Captain reads the balance in the console.
2. **OPEN-2. The cap.** 60M input tokens (USD 3.00) is proposed. Captain sets it.
3. **OPEN-3. People.** The runner (proposed: Pan) and the blind re-scorer (non-Claude and not Ornith; Tifa was ASSAY-001's precedent).
4. **OPEN-4. Host and location.** Which wired machine runs it, and the city to give in the latency note.
5. **OPEN-5. Window and workers.** The run date, and confirmation of 4 workers.
6. **OPEN-6. Public venues.** Where the freeze hash is posted, and where the report is published.
7. **OPEN-7. Legal read.** The full terms, the usage policy, the privacy policy and the data-retention page, covering benchmark publication, publishing raw outputs, and whether any fitted diagnostic counts as developing a model.
8. **OPEN-8. Zero data retention.** Whether to request it before the run.
9. **OPEN-9. Comparison scope.** Option (a), no comparison, is written in. Option (b), a paired Jev arm in the same window, happens only if Captain wants it, and only by amendment before freeze.
10. **OPEN-10. Scope growth.** Noul and Score arms, and a corpus the vendor does not showcase. They stay out of ASSAY-002 unless they are pinned and added before freeze.
11. **OPEN-11. A permutation pass over the full corpus.** Out unless Captain adds it.
12. **OPEN-12. The repo path and its public mirror.**
13. **OPEN-13. Unread pages.** I did not read the SubQ 1.1 Small model card, the SSA research page, or the TypeSafe post linked from the announcement. I also did not read the Files, Conversations, Structured outputs and Function-calling pages, which cover `subq-preview` rather than Snap. If any of them defines `confidence`, probability precision or version pinning, the protocol changes before freeze.

---

## Appendix A: scorer spec (to be frozen as `SPEC-FOR-INDEPENDENT-SCORER.md`)

```
Write two self-contained Python 3 scripts, rescore.py and pairs.py, using only the
standard library and numpy. Print JSON only. Do not explain.

DEFINITIONS
- A "number" is a JSON int or float that is not a boolean, not NaN and not infinite.
- Record shape, one JSON object per line (any field may be missing or malformed;
  the rules say what to do; "tag" may be absent):
  {"id": str, "label": str, "tag": str,
   "response": {"status": int, "ms": float|null, "attempt": int,
                "body": {"model": str,
                         "answers": {"intent": {"type": str, "choice": str,
                                                "probabilities": {option: number},
                                                "confidence": number}},
                         "usage": {"input_tokens": int, "output_tokens": int}}}}
- ECE10(values, outcomes): 10 equal-width bins. Bin 0 covers [0, 0.1]; bin i
  (i = 1..9) covers (i/10, (i+1)/10]. For each bin with n > 0: mean_v = mean(values),
  acc = mean(outcomes), gap = mean_v - acc. ECE10 = sum over populated bins of
  (n / N) * |gap|.
- Wilson(k, n): 95% Wilson score interval, z = 1.959964.

rescore.py
INPUT: argv[1] = responses.jsonl. argv[2] = JSON file holding the list of K label
strings. argv[3] (optional) = the out-of-scope label (e.g. "oos").

R1. records = number of lines. non_200 = records with status != 200; also
    non_200_by_status = {status: count}.
R2. For each status-200 record, note which checks fail:
    a answers.intent is an object
    b answers.intent.type == "choice"
    c choice is a string in the label set
    d probabilities is an object
    e set of probabilities keys == label set
    f every probabilities value is a number in [0, 1]
    g d and f hold and abs(sum(values) - 1) <= 0.02 (if d or f fails, g fails)
    h confidence is a number in [0, 1]
    violations = records failing any of a-h.
    violations_documented = records failing any of a-f.
    violations_undocumented_only = records passing a-f and failing g or h.
    Over records where d and f hold: sum_min, sum_max, and
    sum_off_1e3 = count with abs(sum - 1) > 0.001.
R3. Calibration set = status-200 records where a holds, c holds, d holds, choice is a
    key of probabilities, and probabilities[choice] is a number in [0, 1].
    scored = N = its size. Failing b, e, g or h does NOT remove a record.
    Sort the calibration set by id (ascending string order); use that order below.
R4. For each calibration record: p = probabilities[choice];
    correct = 1 if choice == label else 0.
R5. ECE = ECE10(p, correct). bins = list of {bin, n, mean_p, acc, gap} for populated
    bins. MCE_all = max |gap| over populated bins. MCE_50 = max |gap| over bins with
    n >= 50 (null if none).
R6. ECE_equal_mass: sort the calibration set by (p, id); split into 10 parts with
    numpy.array_split; sum over parts of (n_part / N) * |mean_p - acc|.
R7. Brier = mean over calibration records of the sum over the K labels of
    (q_k - y_k)^2, where q_k = probabilities[k] if it is a number, else 0, and
    y_k = 1 if k == label else 0.
R8. accuracy = mean(correct). mean_p = mean(p). signed_gap = mean_p - accuracy.
R9. direction, over bins with n >= 50: "over" if every one has gap >= 0; "under" if
    every one has gap <= 0; "mixed" otherwise; "undetermined" if there are none.
R10. Bootstrap: rng = numpy.random.default_rng(2002). Repeat 2000 times:
     idx = rng.integers(0, N, size=N); compute ECE10(p[idx], correct[idx]).
     ECE_ci = [2.5th, 97.5th percentile] (numpy.percentile, default linear).
R11. Noise floor: rng = numpy.random.default_rng(2003). Repeat 2000 times:
     y = (rng.random(N) < p).astype(int); compute ECE10(p, y).
     noise_mean = mean; noise_p95 = 95th percentile.
R12. For S in {"gt09": p > 0.9, "ge09": p >= 0.9, "atom1": round(p, 6) == 1.0}:
     n, share = n / N, acc = mean(correct over S) (null if empty),
     wilson = Wilson(sum(correct over S), n).
     floor (S = gt09): wrong_all = N - sum(correct);
     wrong_shipped = n_gt09 - sum(correct over gt09); right_share_shipped = acc of
     gt09; refused_share = 1 - n_gt09 / N.
R13. argmax_exceptions = calibration records where d and f hold and
     p < max(values) - 1e-9.
R14. Latency over status-200 records with attempt == 1 and ms a number:
     latency_median, latency_p95, latency_p99 (numpy.percentile, default linear).
R15. attempts = {attempt: count} over all records. models = {body.model: count} over
     status-200 records. input_tokens_sum = sum of usage.input_tokens over status-200
     records where it is an int.
R16. Confidence (secondary): calibration records where confidence is a number in
     [0, 1]. Sort by (confidence, id); split into 10 parts with numpy.array_split;
     per part: n, mean_confidence, accuracy. conf_monotone = true if accuracy never
     decreases from part 1 to part 10. ECE_conf = ECE10(confidence, correct).
     conf_atom1_share = share with round(confidence, 6) == 1.0.
R17. Out-of-scope, only if argv[3] is given. Over the calibration set:
     oos = (label == argv[3]); inscope = not oos. Report n_oos, n_inscope, acc_oos,
     acc_inscope, mean_p_oos, mean_p_inscope, mean_conf_oos and mean_conf_inscope
     (over records with numeric confidence), and high_p_wrong_oos = (count of oos
     records with correct == 0 and p > 0.9) / n_oos.
     AUROC = (R - n_inscope * (n_inscope + 1) / 2) / (n_inscope * n_oos), where R is
     the sum of the ranks of the in-scope p values among all calibration p values
     (ranks start at 1; tied values get the average of their ranks).

OUTPUT: one JSON object, keys in this order, floats rounded to 4 dp, latency to 1 dp:
records, non_200, non_200_by_status, scored, violations, violations_documented,
violations_undocumented_only, sum_min, sum_max, sum_off_1e3, accuracy, mean_p,
signed_gap, ECE, ECE_ci, noise_mean, noise_p95, ECE_equal_mass, MCE_all, MCE_50,
Brier, direction, bins, gt09, ge09, atom1, floor, argmax_exceptions, latency_median,
latency_p95, latency_p99, attempts, models, input_tokens_sum, conf_deciles,
conf_monotone, ECE_conf, conf_atom1_share, oos (object, or null)

pairs.py
INPUT: argv[1] = file A, argv[2] = file B (both responses.jsonl). Optional
argv[3] = tag to keep from A, argv[4] = tag to keep from B ("-" keeps all).

Q1. Build the R3 calibration set of each file after the tag filter. Join on id; keep
    ids present in both. n_pairs = number joined.
Q2. flips = count where choice_A != choice_B. flip_rate = flips / n_pairs.
Q3. Over flips: both_le09 = count with p_A <= 0.9 and p_B <= 0.9;
    both_lt09 = count with p_A < 0.9 and p_B < 0.9; acc_A_flipped; acc_B_flipped.
Q4. Over stable pairs (same choice): acc_stable; absdp = |p_A - p_B|;
    absdp_median; absdp_gt005_share = share with absdp > 0.05.
Q5. cross_09 = count of joined pairs where exactly one of p_A > 0.9, p_B > 0.9 holds.

OUTPUT keys in this order: n_pairs, flips, flip_rate, both_le09, both_lt09,
acc_A_flipped, acc_B_flipped, acc_stable, absdp_median, absdp_gt005_share, cross_09
```

## Appendix B: ASSAY-001 reference values (historical; not a head-to-head)

These are Jev's figures: `jev-latest`, which resolved to `jev-1.13.0`, one pass, 2026-09-17 by machine clock. Jev is a different model, measured on a different date, at a different version. All values come from the amended scorer (Amendment 2), and Tifa reproduced them with Δ = 0. Sealed run files: Banking77 `b5c96bc1ff6be5efd702d943273a75eaaff7d4b1fc23ecd0b17eb03ad40de978`, CLINC150 `5f5c58b2ca24deb6627f0f7384015c7a7221a4851c4955007651e0006722834b` (both re-hashed 2026-10-12).

| Field | Banking77 | CLINC150 |
|---|---|---|
| Records / scored / non-200 | 3,080 / 3,080 / 0 | 5,500 / 5,496 / 4 (DNS failures on the auditor's side) |
| ECE (10 bins) | 0.0936 | 0.0204 |
| MCE | 0.86 (a single item, in bin (0.1, 0.2]) | 0.06 |
| Brier | 0.3088 | 0.1846 |
| Accuracy | 0.7977 | 0.8812 |
| Type errors at tolerance 0.02 | 0 | 0 |
| Sums more than 1e-3 from 1 | 145 | 368 |
| `choice` not the argmax | 2 | 1 |
| Latency median / p95 / p99 (ms) | 382.3 / 553.7 / 852.1 | 385.9 / 615.3 / 845.1 |
| Top bin (0.9, 1.0] | n 2,129; mean p 0.9857; accuracy 0.9272 | n 3,862; mean p 0.9863; accuracy 0.9614 |
| `confidence` ECE (secondary) | 0.088 | 0.0217 |
| Out-of-scope | n/a | Accuracy 0.723; mean p 0.7903; mean confidence 0.7799 vs 0.9176 in-scope |
| Floor readout (p > 0.9) | Right 79.8% → 92.7%; wrong shipped 623 → 155; 31% refused | n/a |
| Order probe, 2026-09-20 | 16/300 flips (5.3%) vs 0/50; all flips had p < 0.9 on both sides; abs(Δp) > 0.05 on 28.5% of stable items vs 12% in the control | n/a |

- **Latency location.** ASSAY-001's latency was measured from The Woodlands, TX, according to REPORT.md. Its protocol and `score.py` say Plano, TX.
- **New metrics.** The ASSAY-002 scorer adds this table's new metrics at report time, from the sealed files.
- **A correction owed to the ASSAY-001 record.** REPORT.md says "The verdicts do not change under either rule." That is true for C1 but not for C2: the frozen scorer gives 145 C2 violations on Banking77 and 368 on CLINC150 (FAIL), and the amended scorer gives 0 (PASS). This was corrected publicly in `ASSAY-001/ERRATUM-1.md` on 2026-10-12.

**The chamber holds.** 🐦‍⬛ + 🔑