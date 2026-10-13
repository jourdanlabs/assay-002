#!/usr/bin/env python3
"""Extract Appendix A fenced block from the protocol draft verbatim
into assay-002/SPEC-FOR-INDEPENDENT-SCORER.md (protocol 12.5)."""
import hashlib
from pathlib import Path

draft = Path("/Users/sokpyeon/projects/pan-cc/handoffs/assay-002-draft/PROTOCOL-DRAFT-2026-10-12.md")
out = Path("/Users/sokpyeon/projects/assay-002/SPEC-FOR-INDEPENDENT-SCORER.md")

text = draft.read_text()
anchor = text.index("## Appendix A")
start = text.index("```\n", anchor) + len("```\n")
end = text.index("\n```", start)
block = text[start:end] + "\n"

assert block.startswith("Write two self-contained Python 3 scripts"), block[:80]
assert block.rstrip().endswith("cross_09"), block[-80:]
out.write_text(block)
print(f"lines={block.count(chr(10))} bytes={len(block.encode())}")
print(f"sha256={hashlib.sha256(block.encode()).hexdigest()}")
print(f"first={block.splitlines()[0]!r}")
print(f"last={block.splitlines()[-1]!r}")
print(f"draft sha256={hashlib.sha256(draft.read_bytes()).hexdigest()}")
