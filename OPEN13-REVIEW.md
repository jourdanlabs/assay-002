# OPEN-13 read-only page review — ASSAY-002

Reviewer: Toph (runner) · Task: `PAN-TOPH-ASSAY-002-RUNNER-BRIEF-2026-10-12.md` OPEN-13 · Protocol §18 item 13
Fetched and read: 2026-10-12 evening (sealed to this repo 2026-10-13T00:57Z). **Zero API calls; public GETs only, no key used or read.**

**Question:** does any assigned unread page define the Decisions `confidence` field, state probability precision/rounding, or document version pinning for Snap? If yes, stop — protocol changes before freeze.

**Answer: no.** Every page was read in full. Every keyword hit is dispositioned verbatim below. Raw fetches + text extractions in `docs-open13/` (hashes at bottom).

## Method

- Docs pages fetched as raw Markdown from `docs.subq.ai` (URLs from `llms.txt`); site pages fetched as raw HTML from `subq.ai`, tags/scripts stripped mechanically to `.txt`; model-card PDF text extracted with PyMuPDF (22 pages).
- Grep terms (case-insensitive): `confiden`, `probabil`, `calibrat`, `decimal`, `precision`, `round`, `pinned`, `pinning`, `version`, `alias`. Grep located candidates; verdicts rest on the full reads.

## Per-page results

1. **Files** — read both candidate pages in full: *Sending files* (`file-inputs.md`, 13,232 B) and *Files API* (`files-api.md`, 10,793 B). Early-access `subq-preview` Chat/Responses file handling. **Zero hits** for every grep term. Nothing on confidence, probability precision, or pinning.
2. **Conversations** — *Conversations API* (`conversations-api.md`, 10,316 B), stored-conversation CRUD, "no inference runs". **Zero hits.**
3. **Structured outputs** — `structured-outputs.md` (27,471 B, JSON-Schema replies). Two `probabilities` hits, both pointers only: "For a yes/no, category, or rating judgment with probabilities, use the Decisions API instead" and the same line in Related links. No definition, precision, or pinning.
4. **Function calling** — `function-calling.md` (36,483 B, tool use). Only hits are `round` as loop rounds in sample code (`maxFunctionRounds`). Nothing on confidence/probabilities/pinning.
5. **SubQ 1.1 model card** — PDF *SubQ-1.1-Small Technical Report* (`subq-1-1-small-model-card.pdf`, 22 pp, 1,603,722 B) + announcement page *Introducing SubQ 1.1 Small*. Entirely SSA architecture/training/retrieval for the `subq-preview` LLM; nothing about the Decisions API. All hits: "low-precision state storage" (training numerics); "the more confidently outcomes can be attributed" and "The version of the finding we hold with confidence is the weaker one" (rhetorical prose; the PDF's single `version` hit); announcement: "NIAH is the precision test" (retrieval exactness). **No confidence-field definition, no probability precision, no version pinning.**
6. **SSA research page** — *How SSA Makes Long Context Practical* (Research, May 5 2026, upd. May 15; `how-ssa-makes-long-context-practical.html`). Single relevant hit: "numerical precision" as a million-token training-stability constraint. Nothing on Snap fields.
7. **Extra (routing check):** `subq.ai/research` and `subq.ai/ssa` return byte-identical server HTML (SHA-256 `b59372ce…`, 39,375 B) whose text is the Snap homepage/research index (already-read class; corroborates the homepage line "Free 100M tokens for the first 10,000 users" — balance itself is Captain's console read per OPEN-1). Zero hits on the grep terms.

## Limits of this review

- Site pages assessed as server-delivered HTML with scripts stripped; no JS execution. `/research` and `/ssa` are app shells (identical bytes), so any text injected only by client JS beyond the linked article slugs would not be seen. The named research articles were fetched and read at their own slugs. If Pan wants a browser-rendered sweep, that is a separate pass.
- Scope is the brief's six items (Files read as both files pages). The protocol §18 also names a TypeSafe post linked from the announcement; the brief's operative list omits it and it is a third party's page either way. Not read.

## Bottom line for Pan

Nothing in the OPEN-13 set defines `confidence`, states probability precision, or documents version pinning. **No protocol change is triggered on this evidence.** Proceeding to §12 freeze prep per the brief's order; if you read this differently, stop me before the freeze commit — nothing runs before your gate regardless.

## Hashes (SHA-256, files in `docs-open13/`)

```
92892d841aad747e047cafd2c171529e0248899dffd10a2391d2e7c221825b9a  conversations-api.md
ffd7b736f6cd4eb2b72b3b177821d046ee4d18f2d8ac5693fb8b7513b6a183cf  file-inputs.md
59fcf7e349778e38ae65547012ae424b92ffc7494fb73deb7308f12264c88da4  files-api.md
a90a3c1df538c6baf2f2a7296f90c2542a1dd38c79b706880841992a0c240b10  function-calling.md
b8f211b5d53901b0ef010aced331ad7c3747756593c67a25416efd18d73e8ca1  structured-outputs.md
e4974c9b987bf8f26d1e5e0a5a1f712e302ed88c5648bb6a81a7a5f607f87138  subq-1-1-small-model-card.pdf
df73662ae8f1a86de45e2556e9afcf2b1f9ed338cda4a07203ad7af46751239e  model-card.txt (PyMuPDF extraction)
5d7d89dad6636db6a26d1a3992ee80826125b979d1affcabb10ae5a29add9c25  subq-1-1-small-technical-report.html
e551fbd444e8e63c0cebc2aa7eea42d123e74fdf4b43927ff2f9a9aec6c12aa6  how-ssa-makes-long-context-practical.html
b59372ce8dd72dabbb1e7b7677e80480b50d57adbbf0d696f42a5cbe2b97a6e6  research.html (= ssa.html, identical bytes)
```
