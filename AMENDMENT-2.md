# AMENDMENT-2 — ASSAY-002

- **Number:** 2
- **Machine-clock time:** 2026-10-12 23:06 -0500 (CDT)
- **Position:** AFTER the first main-run call (first call 2026-10-12T22:08:48-05:00). Post-run.
- **Reason:** the run departed from the frozen OPEN-4 resolution. `AMENDMENT-1.md` records OPEN-4 as "Captain's Mac, Dallas — **wired**, stable host per the F5 ruling," and §4.2 F5 gives "the run uses a wired, stable host" as the loss-avoidance rationale. The runner's receipt discloses that the session's default route was `en0` (**Wi-Fi**, `inet 192.168.1.89`); Ethernet adapters `en3`–`en5` existed and were not the default route. The runner did not change the route and made no causal claim. §13: any departure the receipt shows that no amendment explains is a gate failure. This amendment explains it.
- **Exact text changed:** none. No protocol text, no rule, no tolerance, no headline rule, and no scorer behavior is changed by this amendment. The frozen rule stands; the departure is recorded and assessed.
- **Headline effect:** none. (The "first line" clause of §13 does not apply; no headline sentence changes.)

## Materiality assessment

1. **Purpose of the wired requirement.** F5's rationale is loss avoidance: network errors are not retried (§8.3), and losses lower n and must be disclosed. It is not a measurement-rule input. No metric definition (Appendix A), no headline rule (§7), and no probe (§6) reads the host interface.
2. **What actually happened.** 10 of 26,596 decision records (0.038%) returned status 0 (`ETIMEDOUT`, errno 60, ~18.06 s, attempt 1, no retry, per §8.3). Every step still completed its planned n. All 13 per-step seals verify. Item ids: `b77-2792`, `b77-0364`–`b77-0367`, `c150-0510`–`c150-0513`, `c150-4279` (also in the runner's receipt and `scores/finding-item-ids.json`).
3. **Latency.** M3 is an observation, not a gated metric; the latency location readout uses the manifest location (`Dallas, TX`), which is true. The limit clause already bounds the result to the artifacts and window examined.
4. **Disclosure carried forward.** The report states the interface deviation in its deviations section, next to the timeout table, with this amendment cited. Nothing is hidden and nothing is re-run: a re-run over Ethernet would change no rule, no n, and no sentence, and the protocol's remedy for losses (disclosure) was already executed by the runner.

## Registration effect

`FREEZE.sha256` gains one entry for this file (`AMENDMENT-2.md`), per §13 ("each amendment gets its own entry in FREEZE.sha256"). The SHA-256 of `FREEZE.sha256` therefore changes from the publicly pre-registered value `ab6a3ed265b6ae8bf3602e99315cf8eb46e3a365e2a327230fa71ac769b75f43` (freeze commit `a161a41`). The new value is computed at commit time and recorded in `GATE.md`; the visible re-post of the updated hash is **Captain's call** (OPEN-6: no agent posts), to happen alongside the publication decision.
