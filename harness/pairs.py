#!/usr/bin/env python3
"""ASSAY-002 primary paired scorer for P1, P2 and P5.

Metrics in the `metrics` object follow Appendix A Q1-Q5 exactly. Inputs are
joined on item id after each file's R3 calibration set and optional tag
filter have been applied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import calibration_records, load_labels, load_records, r4  # noqa: E402


def filter_tag(records, tag):
    if tag in (None, "-"):
        return records
    return [record for record in records if isinstance(record, dict) and record.get("tag") == tag]


def index_calibration(records, labels=None):
    selected = calibration_records(records, labels)
    indexed = {}
    for item in selected:
        if item["id"] in indexed:
            raise SystemExit(f"duplicate calibration id after tag filter: {item['id']}")
        indexed[item["id"]] = item
    return indexed


def quantiles(values):
    if not len(values):
        return {"min": None, "p25": None, "median": None, "p75": None, "p95": None, "max": None}
    values = np.asarray(values, dtype=float)
    return {
        "min": r4(float(np.min(values))),
        "p25": r4(float(np.percentile(values, 25))),
        "median": r4(float(np.percentile(values, 50))),
        "p75": r4(float(np.percentile(values, 75))),
        "p95": r4(float(np.percentile(values, 95))),
        "max": r4(float(np.max(values))),
    }


def compute_pairs(records_a, records_b, labels=None, tag_a="-", tag_b="-"):
    indexed_a = index_calibration(filter_tag(records_a, tag_a), labels)
    indexed_b = index_calibration(filter_tag(records_b, tag_b), labels)
    joined_ids = sorted(set(indexed_a) & set(indexed_b))
    pairs = []
    for item_id in joined_ids:
        a = indexed_a[item_id]
        b = indexed_b[item_id]
        if a["label"] != b["label"]:
            raise SystemExit(f"gold label mismatch for paired id {item_id}")
        pairs.append((a, b))

    flips = [(a, b) for a, b in pairs if a["choice"] != b["choice"]]
    stable = [(a, b) for a, b in pairs if a["choice"] == b["choice"]]
    absdp_stable = [abs(a["p"] - b["p"]) for a, b in stable]
    absdp_all = [abs(a["p"] - b["p"]) for a, b in pairs]

    def mean_or_none(values):
        return float(np.mean(values)) if len(values) else None

    metrics = {
        "n_pairs": len(pairs),
        "flips": len(flips),
        "flip_rate": r4(len(flips) / len(pairs)) if pairs else None,
        "both_le09": int(sum(1 for a, b in flips if a["p"] <= 0.9 and b["p"] <= 0.9)),
        "both_lt09": int(sum(1 for a, b in flips if a["p"] < 0.9 and b["p"] < 0.9)),
        "acc_A_flipped": r4(mean_or_none([a["correct"] for a, _ in flips])) if flips else None,
        "acc_B_flipped": r4(mean_or_none([b["correct"] for _, b in flips])) if flips else None,
        "acc_stable": r4(mean_or_none([a["correct"] for a, _ in stable])) if stable else None,
        "absdp_median": r4(float(np.median(absdp_stable))) if absdp_stable else None,
        "absdp_gt005_share": r4(float(np.mean([value > 0.05 for value in absdp_stable])))
        if absdp_stable
        else None,
        "cross_09": int(sum(1 for a, b in pairs if (a["p"] > 0.9) != (b["p"] > 0.9))),
    }
    return {
        "metrics": metrics,
        "supplementary": {
            "absdp_all_quantiles": quantiles(absdp_all),
            "absdp_stable_quantiles": quantiles(absdp_stable),
        },
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="ASSAY-002 primary paired scorer")
    parser.add_argument("file_a")
    parser.add_argument("file_b")
    parser.add_argument("tag_a", nargs="?", default="-")
    parser.add_argument("tag_b", nargs="?", default="-")
    parser.add_argument("--labels", default=None, help="frozen label JSON; inferred from requests if omitted")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    path_a = Path(args.file_a)
    path_b = Path(args.file_b)
    labels = load_labels(Path(args.labels)) if args.labels else None
    result = compute_pairs(
        load_records(path_a),
        load_records(path_b),
        labels=labels,
        tag_a=args.tag_a,
        tag_b=args.tag_b,
    )
    output = {
        "scorer": {
            "name": "assay-002-primary-pairs.py",
            "file": "harness/pairs.py",
            "sha256": file_sha256(Path(__file__)),
            "score_sha256": file_sha256(Path(__file__).with_name("score.py")),
        },
        "inputs": {
            "file_a": {"path": str(path_a), "sha256": file_sha256(path_a), "tag": args.tag_a},
            "file_b": {"path": str(path_b), "sha256": file_sha256(path_b), "tag": args.tag_b},
            "labels": (
                {"path": str(args.labels), "sha256": file_sha256(Path(args.labels))}
                if args.labels
                else None
            ),
        },
        **result,
    }
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(output, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {output_path}")
    else:
        print(json.dumps(output, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
