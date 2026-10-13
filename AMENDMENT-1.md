# AMENDMENT-1 — Freeze declaration and OPEN-item resolutions

**Number:** 1 · **Date:** 2026-10-12 21:38 CDT (machine clock: `2026-10-12 21:38:29 -0500`) · **Author of record:** Captain Leland Jourdan II, by ratification · **Drafted by:** Pan 🐦‍⬛🔑 (coordinator seat) · **Reason:** the freeze gate (Claude, final close) found the `7c59dd2` candidate technically clean but administratively blocked: `PROTOCOL.md` still carried its DRAFT banner and the thirteen OPEN items, though ruled at 21:15 in `PAN-TOPH-ASSAY-002-RUNNER-BRIEF-2026-10-12.md`, had never been recorded in the pinned record. This amendment does not change any §7 headline sentence.

## 1. Freeze declaration

As of 2026-10-12 21:38 CDT, Captain **ratified** the resolutions below (his word, in session, recorded in the chamber session log). The freeze state is **declared**. The DRAFT banner at `PROTOCOL.md` line 3 and the `Frozen | Not yet…` header cell are **superseded** by this amendment; the protocol text itself is unchanged to preserve byte-identity with the reviewed draft. `PROTOCOL.md`, `SPEC-FOR-INDEPENDENT-SCORER.md`, the corpora, labels, docs and harness remain pinned exactly as in commit `7c59dd2fa42f462daa624e49e485b6f4b5ae7570`. This file is added to `FREEZE.sha256` per §13. The public pre-registration hash is the SHA-256 of the updated `FREEZE.sha256`, computed by the re-gate after this commit.

**Condition:** Bulma's non-Claude pre-freeze read of the protocol was requested 2026-10-12 21:27 CDT and has not landed. This freeze holds if her read produces no protocol change; any change she produces is handled as a further amendment and re-gates.

## 2. OPEN-item resolutions (each: resolved or cut, in writing)

| Item | Disposition | Resolution |
|---|---|---|
| OPEN-1 free tokens | **resolved** | Run on Captain's free preview tokens (first-10,000-users grant). Captain reads his console balance before run step 4. Expected spend ≈ $1.76 at list price against a 60M-token cap ($3.00). |
| OPEN-2 cap | **resolved** | **60,000,000 input tokens.** Set by Captain, ratified here. Hardcoded in `run.py`'s `CapMeter` with the 80%-projection stop before `drift-start`. |
| OPEN-3 people | **resolved** | Runner: **Toph** (Muse). Blind re-scorer: **Bulma** (non-Claude, not Ornith) — the independence leg. Gate: **Pan** (final close on Claude). Supersedes §11's "Proposed: Pan." |
| OPEN-4 host | **resolved** | Captain's Mac, Dallas — wired, stable host per the F5 ruling. |
| OPEN-5 window, workers | **resolved** | One uninterrupted session, firing immediately after the freeze hash is public; never Friday sundown → Saturday sundown. **4 workers** (`run.py` default), recorded in `MANIFEST.json`. |
| OPEN-6 venue | **resolved** | The SHA-256 of the updated `FREEZE.sha256` is posted publicly before the first API call: the **assay-002 GitHub repo** (freeze commit) plus **donttrustme.ai**. Captain gives the explicit "post it"; no agent posts. |
| OPEN-7 legal / fitted recalibration | **cut** | **No fitted temperature, Platt, isotonic or CORP map is published** unless counsel (Chuck) clears SubQ's terms in writing before publication. ECE/Brier measurement proceeds; the keyword read found no benchmark-publication clause; the full legal read stands as a publication gate. |
| OPEN-8 zero retention | **cut** | No zero-retention request. Inputs are public, licensed corpus text (CC-BY-4.0 / CC-BY-3.0); retention by SubQ is acceptable and disclosed. |
| OPEN-9 paired Jev arm | **cut** | Out of scope. Jev appears only as a labeled historical reference (ASSAY-001). |
| OPEN-10 new corpora / Noul + Score arms | **cut** | Deferred to ASSAY-003. |
| OPEN-11 full-corpus permutation pass | **cut** | P2's option-order pairs give the like-for-like flip rate. |
| OPEN-12 repo | **resolved** | `~/projects/assay-002` (`jourdanlabs/assay-002` mirror at publication time). |
| OPEN-13 docs read | **resolved** | Toph's read (`OPEN13-REVIEW.md`) found no definition of `confidence`, no probability precision, no version pinning; no protocol change. Independently verified by the freeze gate: exactly two `confiden` hits in the corpus, both rhetorical prose. |

## 3. Disclosure carried into the pinned record (launch-post hash)

§12.4's reference hash for the launch-post plain-text capture (`1583ec9c…` in the draft) does not match the frozen capture (`9d25ea04…`). The prior capture no longer exists, so the difference is unrecoverable — whether the page changed or only the extraction method did cannot be established. What is established: the frozen capture is reproducible byte-identically from the pinned raw HTML via the documented `prep/open13_strip.py` algorithm, and every protocol claim resting on the launch post holds against the frozen capture (zero occurrences of `calibrat`; the "~1 second" quote present; vendor figures 91.5 and 80.6 present). This disclosure is also in `docs/CAPTURE.json`, pinned via `DOCS.sha256`. A byte-provenance note, not a science gap.

## 4. What this amendment does not do

It makes no API call, touches no key, changes no harness or scorer byte, and decides nothing about publication (§15–§16). The run fires only after the re-gate returns READY and Captain says "post it."

🐦‍⬛ + 🔑 Pan (coordinator), for the Captain's ratification
