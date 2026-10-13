#!/usr/bin/env python3
import json
import math
import sys

import numpy as np


def is_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def load_calibration(path, tag):
    items = {}
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            raw = json.loads(line)
            record = raw if isinstance(raw, dict) else {}
            if tag != "-" and record.get("tag") != tag:
                continue
            response = record.get("response")
            if not isinstance(response, dict) or response.get("status") != 200:
                continue
            body = response.get("body")
            answers = body.get("answers") if isinstance(body, dict) else None
            intent = answers.get("intent") if isinstance(answers, dict) else None
            if not isinstance(intent, dict):
                continue
            choice = intent.get("choice")
            probabilities = intent.get("probabilities")
            if (
                not isinstance(choice, str)
                or not isinstance(probabilities, dict)
                or choice not in probabilities
            ):
                continue
            p = probabilities.get(choice)
            if not is_number(p) or not 0.0 <= p <= 1.0:
                continue
            item_id = record.get("id")
            if not isinstance(item_id, str):
                item_id = json.dumps(
                    item_id, sort_keys=True, separators=(",", ":")
                )
            items[item_id] = {
                "choice": choice,
                "p": float(p),
                "correct": int(choice == record.get("label")),
            }
    return items


def mean_or_none(values):
    return float(np.mean(values)) if len(values) else None


def rounded(value):
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return round(value, 4)
    return value


def compare(items_a, items_b):
    joined_ids = sorted(set(items_a) & set(items_b))
    joined = [(items_a[item_id], items_b[item_id]) for item_id in joined_ids]
    flipped = [(a, b) for a, b in joined if a["choice"] != b["choice"]]
    stable = [(a, b) for a, b in joined if a["choice"] == b["choice"]]
    absolute_deltas = [abs(a["p"] - b["p"]) for a, b in stable]

    output = {
        "n_pairs": len(joined),
        "flips": len(flipped),
        "flip_rate": len(flipped) / len(joined) if joined else None,
        "both_le09": sum(a["p"] <= 0.9 and b["p"] <= 0.9 for a, b in flipped),
        "both_lt09": sum(a["p"] < 0.9 and b["p"] < 0.9 for a, b in flipped),
        "acc_A_flipped": mean_or_none([a["correct"] for a, _ in flipped]),
        "acc_B_flipped": mean_or_none([b["correct"] for _, b in flipped]),
        "acc_stable": mean_or_none([a["correct"] for a, _ in stable]),
        "absdp_median": (
            float(np.percentile(absolute_deltas, 50))
            if absolute_deltas
            else None
        ),
        "absdp_gt005_share": (
            sum(value > 0.05 for value in absolute_deltas) / len(absolute_deltas)
            if absolute_deltas
            else None
        ),
        "cross_09": sum((a["p"] > 0.9) != (b["p"] > 0.9) for a, b in joined),
    }
    return {key: rounded(value) for key, value in output.items()}


def main():
    if len(sys.argv) not in (3, 4, 5):
        raise SystemExit("usage: pairs.py file-a file-b [tag-a [tag-b]]")
    tag_a = sys.argv[3] if len(sys.argv) >= 4 else "-"
    tag_b = sys.argv[4] if len(sys.argv) >= 5 else "-"
    result = compare(
        load_calibration(sys.argv[1], tag_a),
        load_calibration(sys.argv[2], tag_b),
    )
    print(json.dumps(result, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
