#!/usr/bin/env python3
"""ASSAY-002 freeze prep 12.2 + 12.3: label lists + 300 permutations.

Sources are the assay-002 corpus copies (hash-verified). Permutation
construction is protocol section 6.2 verbatim; verification target is
assay-001 raw/permutation-2026-09-20 order_first5. Writes the
permutations file ONLY on a 300/300 match; otherwise exits 1 (STOP).
Stdlib only. Prints every count. Zero API calls.
"""
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

A2 = Path("/Users/sokpyeon/projects/assay-002")
A1_PERM = Path("/Users/sokpyeon/projects/assay-001/raw/permutation-2026-09-20/responses.jsonl")
SEED = 20260920
N = 300


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --- 12.2 labels ---
categories = json.load(open(A2 / "corpus/banking77/categories.json"))
assert isinstance(categories, list) and len(categories) == 77, len(categories)
banking_labels = list(categories)

names = json.load(open(A2 / "corpus/clinc150/intent_names.json"))
assert isinstance(names, dict) and len(names) == 151, len(names)
assert all(str(i) in names for i in range(151))
clinc_labels = [names[str(i)] for i in range(151)]
assert clinc_labels[42] == "oos", clinc_labels[42]

(A2 / "labels/banking77.json").write_text(json.dumps(banking_labels, indent=1) + "\n")
(A2 / "labels/clinc150.json").write_text(json.dumps(clinc_labels, indent=1) + "\n")
print(f"banking77 labels: {len(banking_labels)} sha256={sha256(A2 / 'labels/banking77.json')}")
print(f"clinc150 labels: {len(clinc_labels)} sha256={sha256(A2 / 'labels/clinc150.json')}")

with open(A2 / "corpus/banking77/test.csv", newline="") as f:
    rows = list(csv.DictReader(f))
print(f"banking77 test rows: {len(rows)}")
assert len(rows) == 3080
assert all(r["category"] in banking_labels for r in rows)

# --- 12.3 permutations (section 6.2 construction) ---
rng = random.Random(SEED)
perms = []
for i in range(N):
    shuffled = banking_labels[:]
    rng.shuffle(shuffled)
    perms.append({"id": f"b77-{i:04d}", "options": shuffled})

sealed = {}
for line in open(A1_PERM):
    r = json.loads(line)
    if r.get("tag") == "shuffled":
        sealed[r["id"]] = r["order_first5"]
print(f"sealed shuffled records: {len(sealed)}")
matched = sum(1 for p in perms if sealed.get(p["id"]) == p["options"][:5])
print(f"order_first5 matched: {matched}/{N}")
if matched != N:
    print("STOP: permutation mismatch — permutations file NOT written", file=sys.stderr)
    sys.exit(1)

out = {"seed": SEED, "n": N, "items": perms}
(A2 / "labels/b77-permutations-300.json").write_text(json.dumps(out, indent=1) + "\n")
print(f"permutations written sha256={sha256(A2 / 'labels/b77-permutations-300.json')}")
print("OK")
