#!/usr/bin/env python3
"""ASSAY-002 primary scorer.

The metric definitions are Appendix A of the frozen protocol, also shipped as
SPEC-FOR-INDEPENDENT-SCORER.md. This program has no model anywhere in it. It
scores one responses.jsonl at a time and can mechanically aggregate completed
pass score files into the registered headline sentences in protocol section 7.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SUM_TOLERANCE = 0.02
SCORER_NAME = "assay-002-primary-score.py"
DISPLAY_CORPUS = {"banking77": "Banking77", "clinc150": "CLINC150"}


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def r4(value):
    if value is None:
        return None
    result = round(float(value), 4)
    return 0.0 if result == 0 else result


def r1(value):
    if value is None:
        return None
    result = round(float(value), 1)
    return 0.0 if result == 0 else result


def canonical_key(value) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def sorted_counts(counter):
    def sort_key(key):
        try:
            return (0, float(key), key)
        except Exception:
            return (1, 0.0, key)

    return {key: int(counter[key]) for key in sorted(counter, key=sort_key)}


def bin_indices(values):
    values = np.asarray(values, dtype=float)
    indices = np.ceil(values * 10).astype(int) - 1
    indices[values == 0] = 0
    return np.clip(indices, 0, 9)


def ece10(values, outcomes):
    values = np.asarray(values, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)
    n_total = len(values)
    if n_total == 0:
        return None, []
    indices = bin_indices(values)
    counts = np.bincount(indices, minlength=10)
    value_sums = np.bincount(indices, weights=values, minlength=10)
    outcome_sums = np.bincount(indices, weights=outcomes, minlength=10)
    ece = 0.0
    bins = []
    for index in range(10):
        n = int(counts[index])
        if n == 0:
            continue
        mean_p = float(value_sums[index] / n)
        acc = float(outcome_sums[index] / n)
        gap = mean_p - acc
        ece += (n / n_total) * abs(gap)
        bins.append({"bin": index, "n": n, "mean_p": mean_p, "acc": acc, "gap": gap})
    return float(ece), bins


def wilson(k, n):
    if n == 0:
        return [None, None]
    z = 1.959964
    p = k / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return [max(0.0, center - half), min(1.0, center + half)]


def get_intent(record):
    if not isinstance(record, dict):
        return None
    response = record.get("response")
    if not isinstance(response, dict):
        return None
    body = response.get("body")
    if not isinstance(body, dict):
        return None
    answers = body.get("answers")
    if not isinstance(answers, dict):
        return None
    return answers.get("intent")


def check_record(record, label_set):
    intent = get_intent(record)
    checks = {letter: False for letter in "abcdefgh"}
    if not isinstance(intent, dict):
        return checks, intent, None, None, None
    checks["a"] = True
    choice = intent.get("choice")
    probabilities = intent.get("probabilities")
    confidence = intent.get("confidence")
    checks["b"] = intent.get("type") == "choice"
    checks["c"] = isinstance(choice, str) and choice in label_set
    checks["d"] = isinstance(probabilities, dict)
    if checks["d"]:
        checks["e"] = set(probabilities.keys()) == label_set
        checks["f"] = all(is_number(v) and 0 <= float(v) <= 1 for v in probabilities.values())
        checks["g"] = bool(checks["f"] and abs(sum(float(v) for v in probabilities.values()) - 1.0) <= SUM_TOLERANCE)
    checks["h"] = is_number(confidence) and 0 <= float(confidence) <= 1
    return checks, intent, choice, probabilities, confidence


def inferred_label_set(record, probabilities):
    request = record.get("request") if isinstance(record, dict) else None
    if isinstance(request, dict):
        questions = request.get("questions")
        intent = questions.get("intent") if isinstance(questions, dict) else None
        criteria = intent.get("criteria") if isinstance(intent, dict) else None
        if isinstance(criteria, dict) and criteria:
            return set(criteria.keys())
    return set(probabilities.keys()) if isinstance(probabilities, dict) else set()


def calibration_records(records, labels=None):
    """Return the R3 calibration set, sorted by item id.

    pairs.py uses this helper. When labels are omitted (the independent
    pairs interface), the option set is inferred record by record from the
    request criteria, falling back to probability keys.
    """
    supplied = set(labels) if labels is not None else None
    selected = []
    for record in records:
        if not isinstance(record, dict):
            continue
        response = record.get("response")
        if not isinstance(response, dict) or response.get("status") != 200:
            continue
        intent = get_intent(record)
        if not isinstance(intent, dict):
            continue
        choice = intent.get("choice")
        probabilities = intent.get("probabilities")
        options = supplied if supplied is not None else inferred_label_set(record, probabilities)
        if not isinstance(choice, str) or choice not in options:
            continue
        if not isinstance(probabilities, dict) or choice not in probabilities:
            continue
        p = probabilities[choice]
        if not is_number(p) or not 0 <= float(p) <= 1:
            continue
        item_id = record.get("id")
        selected.append(
            {
                "id": item_id if isinstance(item_id, str) else "",
                "label": record.get("label"),
                "choice": choice,
                "p": float(p),
                "correct": int(choice == record.get("label")),
                "confidence": intent.get("confidence"),
                "probabilities": probabilities,
            }
        )
    selected.sort(key=lambda item: item["id"])
    return selected


def average_ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        average = (start + 1 + end) / 2.0
        for position in range(start, end):
            ranks[order[position]] = average
        start = end
    return ranks


def rounded_bins(bins):
    return [
        {
            "bin": row["bin"],
            "n": row["n"],
            "mean_p": r4(row["mean_p"]),
            "acc": r4(row["acc"]),
            "gap": r4(row["gap"]),
        }
        for row in bins
    ]


def analyze_records(records, labels, oos_label=None):
    label_set = set(labels)
    status_counts = Counter()
    attempt_counts = Counter()
    model_counts = Counter()
    non_200 = 0
    violations = 0
    violations_documented = 0
    violations_undocumented_only = 0
    violation_records = []
    sums = []
    latency = []
    input_tokens_sum = 0
    calibration = []
    argmax_exception_ids = []
    timestamps = []

    for record in records:
        record_dict = record if isinstance(record, dict) else {}
        response = record_dict.get("response")
        if not isinstance(response, dict):
            response = {}
        status = response.get("status")
        status_counts[canonical_key(status)] += 1
        attempt_counts[canonical_key(response.get("attempt"))] += 1
        ts = record_dict.get("ts")
        if is_number(ts):
            timestamps.append(float(ts))
        if status != 200:
            non_200 += 1
            continue

        body = response.get("body")
        model = body.get("model") if isinstance(body, dict) else None
        model_counts[canonical_key(model)] += 1
        usage = body.get("usage") if isinstance(body, dict) else None
        if isinstance(usage, dict) and type(usage.get("input_tokens")) is int:
            input_tokens_sum += usage["input_tokens"]
        attempt = response.get("attempt")
        if type(attempt) is int and attempt == 1 and is_number(response.get("ms")):
            latency.append(float(response["ms"]))

        checks, _intent, choice, probabilities, confidence = check_record(record_dict, label_set)
        failed = [letter for letter in "abcdefgh" if not checks[letter]]
        if failed:
            violations += 1
            if any(letter in failed for letter in "abcdef"):
                violations_documented += 1
            else:
                violations_undocumented_only += 1
            violation_records.append({"id": record_dict.get("id"), "checks_failed": failed})
        if checks["d"] and checks["f"]:
            sums.append(sum(float(v) for v in probabilities.values()))

        is_calibration = bool(
            checks["a"]
            and checks["c"]
            and checks["d"]
            and isinstance(choice, str)
            and choice in probabilities
            and is_number(probabilities[choice])
            and 0 <= float(probabilities[choice]) <= 1
        )
        if is_calibration:
            item_id = record_dict.get("id")
            entry = {
                "id": item_id if isinstance(item_id, str) else "",
                "label": record_dict.get("label"),
                "choice": choice,
                "p": float(probabilities[choice]),
                "correct": int(choice == record_dict.get("label")),
                "confidence": confidence,
                "probabilities": probabilities,
                "_checks": checks,
            }
            calibration.append(entry)
            if checks["d"] and checks["f"] and entry["p"] < max(float(v) for v in probabilities.values()) - 1e-9:
                argmax_exception_ids.append(entry["id"])

    calibration.sort(key=lambda item: item["id"])
    violation_records.sort(key=lambda item: str(item.get("id")))
    argmax_exception_ids.sort()
    n = len(calibration)
    p = np.asarray([item["p"] for item in calibration], dtype=float)
    correct = np.asarray([item["correct"] for item in calibration], dtype=float)

    ece, bins = ece10(p, correct)
    mce_all = max((abs(row["gap"]) for row in bins), default=None)
    mce_50 = max((abs(row["gap"]) for row in bins if row["n"] >= 50), default=None)
    accuracy = float(np.mean(correct)) if n else None
    mean_p = float(np.mean(p)) if n else None
    signed_gap = mean_p - accuracy if n else None

    if n:
        ordered = sorted(calibration, key=lambda item: (item["p"], item["id"]))
        equal_mass = 0.0
        for part in np.array_split(np.arange(n), 10):
            if len(part) == 0:
                continue
            part_p = np.asarray([ordered[int(i)]["p"] for i in part], dtype=float)
            part_y = np.asarray([ordered[int(i)]["correct"] for i in part], dtype=float)
            equal_mass += (len(part) / n) * abs(float(np.mean(part_p)) - float(np.mean(part_y)))
        brier = float(
            np.mean(
                [
                    sum(
                        (
                            (float(item["probabilities"][label]) if is_number(item["probabilities"].get(label)) else 0.0)
                            - (1.0 if label == item["label"] else 0.0)
                        )
                        ** 2
                        for label in labels
                    )
                    for item in calibration
                ]
            )
        )
        rng = np.random.default_rng(2002)
        bootstrap = []
        for _ in range(2000):
            idx = rng.integers(0, n, size=n)
            value, _ = ece10(p[idx], correct[idx])
            bootstrap.append(value)
        ece_ci = [float(np.percentile(bootstrap, 2.5)), float(np.percentile(bootstrap, 97.5))]
        rng = np.random.default_rng(2003)
        noise = []
        for _ in range(2000):
            simulated = (rng.random(n) < p).astype(int)
            value, _ = ece10(p, simulated)
            noise.append(value)
        noise_mean = float(np.mean(noise))
        noise_p95 = float(np.percentile(noise, 95))
    else:
        equal_mass = brier = noise_mean = noise_p95 = None
        ece_ci = [None, None]

    eligible_bins = [row for row in bins if row["n"] >= 50]
    if not eligible_bins:
        direction = "undetermined"
    elif all(row["gap"] >= 0 for row in eligible_bins):
        direction = "over"
    elif all(row["gap"] <= 0 for row in eligible_bins):
        direction = "under"
    else:
        direction = "mixed"

    def group(mask):
        count = int(np.sum(mask)) if n else 0
        successes = int(np.sum(correct[mask])) if count else 0
        return {
            "n": count,
            "share": r4(count / n) if n else None,
            "acc": r4(successes / count) if count else None,
            "wilson": [r4(value) for value in wilson(successes, count)],
        }

    if n:
        gt09_mask = p > 0.9
        ge09_mask = p >= 0.9
        atom_mask = np.asarray([round(float(value), 6) == 1.0 for value in p])
        gt09 = group(gt09_mask)
        ge09 = group(ge09_mask)
        atom1 = group(atom_mask)
        wrong_all = int(n - np.sum(correct))
        wrong_shipped = int(np.sum(gt09_mask) - np.sum(correct[gt09_mask]))
        floor = {
            "wrong_all": wrong_all,
            "wrong_shipped": wrong_shipped,
            "right_share_shipped": gt09["acc"],
            "refused_share": r4(1 - np.sum(gt09_mask) / n),
        }
    else:
        gt09 = ge09 = atom1 = {"n": 0, "share": None, "acc": None, "wilson": [None, None]}
        floor = {
            "wrong_all": 0,
            "wrong_shipped": 0,
            "right_share_shipped": None,
            "refused_share": None,
        }

    conf_items = [
        item
        for item in calibration
        if is_number(item["confidence"]) and 0 <= float(item["confidence"]) <= 1
    ]
    conf_items.sort(key=lambda item: (float(item["confidence"]), item["id"]))
    conf_deciles = []
    if conf_items:
        for part in np.array_split(np.arange(len(conf_items)), 10):
            if len(part) == 0:
                conf_deciles.append({"n": 0, "mean_confidence": None, "accuracy": None})
                continue
            selected = [conf_items[int(i)] for i in part]
            conf_deciles.append(
                {
                    "n": len(selected),
                    "mean_confidence": r4(np.mean([float(x["confidence"]) for x in selected])),
                    "accuracy": r4(np.mean([x["correct"] for x in selected])),
                }
            )
        conf_values = np.asarray([float(x["confidence"]) for x in conf_items], dtype=float)
        conf_correct = np.asarray([x["correct"] for x in conf_items], dtype=float)
        ece_conf, _ = ece10(conf_values, conf_correct)
        accuracies = [row["accuracy"] for row in conf_deciles if row["n"]]
        conf_monotone = all(accuracies[i] <= accuracies[i + 1] for i in range(len(accuracies) - 1))
        conf_atom_share = float(np.mean([round(float(x), 6) == 1.0 for x in conf_values]))
    else:
        conf_deciles = [{"n": 0, "mean_confidence": None, "accuracy": None} for _ in range(10)]
        ece_conf = None
        conf_monotone = True
        conf_atom_share = None

    oos = None
    if oos_label is not None:
        is_oos = np.asarray([item["label"] == oos_label for item in calibration], dtype=bool)
        in_scope = ~is_oos
        n_oos = int(np.sum(is_oos))
        n_inscope = int(np.sum(in_scope))

        def mean_or_none(values):
            return float(np.mean(values)) if len(values) else None

        def mean_conf(mask):
            vals = [
                float(item["confidence"])
                for item, keep in zip(calibration, mask)
                if keep and is_number(item["confidence"])
            ]
            return mean_or_none(vals)

        if n_oos and n_inscope:
            ranks = average_ranks(list(p))
            rank_sum = sum(rank for rank, keep in zip(ranks, in_scope) if keep)
            auroc = (rank_sum - n_inscope * (n_inscope + 1) / 2) / (n_inscope * n_oos)
        else:
            auroc = None
        oos = {
            "n_oos": n_oos,
            "n_inscope": n_inscope,
            "acc_oos": r4(mean_or_none(correct[is_oos])) if n_oos else None,
            "acc_inscope": r4(mean_or_none(correct[in_scope])) if n_inscope else None,
            "mean_p_oos": r4(mean_or_none(p[is_oos])) if n_oos else None,
            "mean_p_inscope": r4(mean_or_none(p[in_scope])) if n_inscope else None,
            "mean_conf_oos": r4(mean_conf(is_oos)),
            "mean_conf_inscope": r4(mean_conf(in_scope)),
            "high_p_wrong_oos": r4(
                int(np.sum(is_oos & (correct == 0) & (p > 0.9))) / n_oos
            )
            if n_oos
            else None,
            "AUROC": r4(auroc),
        }

    latency_values = np.asarray(latency, dtype=float)
    metrics = {
        "records": len(records),
        "non_200": non_200,
        "non_200_by_status": {
            key: status_counts[key] for key in sorted(status_counts) if key != "200"
        },
        "scored": n,
        "violations": violations,
        "violations_documented": violations_documented,
        "violations_undocumented_only": violations_undocumented_only,
        "sum_min": r4(min(sums)) if sums else None,
        "sum_max": r4(max(sums)) if sums else None,
        "sum_off_1e3": int(sum(1 for value in sums if abs(value - 1.0) > 0.001)),
        "accuracy": r4(accuracy),
        "mean_p": r4(mean_p),
        "signed_gap": r4(signed_gap),
        "ECE": r4(ece),
        "ECE_ci": [r4(ece_ci[0]), r4(ece_ci[1])],
        "noise_mean": r4(noise_mean),
        "noise_p95": r4(noise_p95),
        "ECE_equal_mass": r4(equal_mass),
        "MCE_all": r4(mce_all),
        "MCE_50": r4(mce_50),
        "Brier": r4(brier),
        "direction": direction,
        "bins": rounded_bins(bins),
        "gt09": gt09,
        "ge09": ge09,
        "atom1": atom1,
        "floor": floor,
        "argmax_exceptions": len(argmax_exception_ids),
        "latency_median": r1(np.percentile(latency_values, 50)) if len(latency_values) else None,
        "latency_p95": r1(np.percentile(latency_values, 95)) if len(latency_values) else None,
        "latency_p99": r1(np.percentile(latency_values, 99)) if len(latency_values) else None,
        "attempts": sorted_counts(attempt_counts),
        "models": sorted_counts(model_counts),
        "input_tokens_sum": int(input_tokens_sum),
        "conf_deciles": conf_deciles,
        "conf_monotone": bool(conf_monotone),
        "ECE_conf": r4(ece_conf),
        "conf_atom1_share": r4(conf_atom_share),
        "oos": oos,
    }
    return {
        "metrics": metrics,
        "violation_records": violation_records,
        "argmax_exception_ids": argmax_exception_ids,
        "record_ts_min": min(timestamps) if timestamps else None,
        "record_ts_max": max(timestamps) if timestamps else None,
        "plot_bins": bins,
    }


def load_records(path: Path):
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            records.append({})
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            records.append({})
    return records


def load_labels(path: Path):
    labels = json.load(open(path, encoding="utf-8"))
    if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
        raise SystemExit(f"{path} is not a JSON list of label strings")
    if len(labels) != len(set(labels)):
        raise SystemExit(f"{path} contains duplicate labels")
    return labels


def scorer_metadata():
    return {
        "name": SCORER_NAME,
        "file": "harness/score.py",
        "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sum_tolerance": SUM_TOLERANCE,
    }


def infer_pass(records, manifest):
    candidates = []
    if isinstance(manifest, dict):
        candidates.extend([manifest.get("step"), manifest.get("tag")])
        tags = manifest.get("tags")
        if isinstance(tags, list):
            candidates.extend(tags)
    candidates.extend(record.get("tag") for record in records if isinstance(record, dict))
    for value in candidates:
        if isinstance(value, str) and value.startswith("pass") and value[-1:].isdigit():
            return int(value[-1])
    return None


def write_reliability_plot(path: Path, bins, title: str):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], "--", color="#999999", label="perfect calibration")
    xs = [row["mean_p"] for row in bins]
    ys = [row["acc"] for row in bins]
    ax.plot(xs, ys, "o-", color="#25374b", label="Snap")
    for row in bins:
        ax.annotate(
            str(row["n"]),
            (row["mean_p"], row["acc"]),
            fontsize=7,
            xytext=(3, 3),
            textcoords="offset points",
        )
    ax.set_xlabel("probability of chosen option (bin mean)")
    ax.set_ylabel("accuracy in bin")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(title)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def score_one(args) -> int:
    input_path = Path(args.input)
    labels_path = Path(args.labels)
    labels = load_labels(labels_path)
    records = load_records(input_path)
    manifest = None
    manifest_path = Path(args.manifest) if args.manifest else input_path.parent / "MANIFEST.json"
    if manifest_path.exists():
        try:
            manifest = json.load(open(manifest_path, encoding="utf-8"))
        except Exception:
            manifest = None
    oos_label = args.oos
    if oos_label is None and not args.no_oos and "oos" in labels:
        oos_label = "oos"
    analysis = analyze_records(records, labels, oos_label=oos_label)
    manifest_subset = None
    if isinstance(manifest, dict):
        manifest_subset = {
            key: manifest.get(key)
            for key in (
                "step",
                "corpus",
                "tags",
                "location",
                "host",
                "workers_initial",
                "workers_current",
                "started",
                "finished",
                "completed",
                "protocol_sha256",
            )
        }
    completed = args.completed
    if completed is None:
        completed = bool(manifest.get("completed")) if isinstance(manifest, dict) and "completed" in manifest else True
    corpus = args.corpus or (manifest.get("corpus") if isinstance(manifest, dict) else None) or labels_path.stem
    pass_number = args.pass_number if args.pass_number is not None else infer_pass(records, manifest)
    location = manifest.get("location") if isinstance(manifest, dict) else None
    output = {
        "scorer": scorer_metadata(),
        "corpus": corpus,
        "pass": pass_number,
        "completed": bool(completed),
        "input": {
            "path": str(input_path),
            "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        },
        "labels": {
            "path": str(labels_path),
            "sha256": hashlib.sha256(labels_path.read_bytes()).hexdigest(),
            "count": len(labels),
        },
        "manifest": manifest_subset,
        "latency_location": location,
        "latency_note": f"observed end-to-end from {location}; includes network" if location else None,
        "record_ts_min": analysis["record_ts_min"],
        "record_ts_max": analysis["record_ts_max"],
        "metrics": analysis["metrics"],
        "violation_records": analysis["violation_records"],
        "argmax_exception_ids": analysis["argmax_exception_ids"],
    }
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(output, indent=1) + "\n", encoding="utf-8")
        if not args.no_plot and analysis["plot_bins"]:
            plot_path = output_path.with_name(output_path.stem + "-reliability.png")
            title = f"ASSAY-002 · {DISPLAY_CORPUS.get(corpus, corpus)}"
            if pass_number is not None:
                title += f" · pass {pass_number}"
            write_reliability_plot(plot_path, analysis["plot_bins"], title)
            print(f"wrote {plot_path}")
        print(f"wrote {output_path}")
    else:
        print(json.dumps(output, indent=1))
    return 0


def _fmt(value) -> str:
    return f"{float(value):.4f}"


def calibration_sentence(corpus: str, entries):
    display = DISPLAY_CORPUS.get(corpus, corpus)
    completed = [
        entry
        for entry in sorted(entries, key=lambda item: item["pass"])
        if entry.get("completed") and entry.get("metrics", {}).get("ECE") is not None
    ]
    k = len(completed)
    if k == 0:
        return f"On {display}, 0 of 3 passes completed, so no ECE sentence can be formed."
    by_pass = {entry["pass"]: entry for entry in completed}
    eces = [float(entry["metrics"]["ECE"]) for entry in completed]
    minimum, maximum = min(eces), max(eces)
    range_text = f"{_fmt(minimum)}–{_fmt(maximum)}"
    pass_phrase = "over three passes" if k == 3 else f"over {k} completed passes"
    pass1 = by_pass.get(1)

    if maximum <= 0.05:
        if pass1 is not None:
            core = (
                f"On {display}, Snap's chosen-option probabilities measured ECE "
                f"{_fmt(pass1['metrics']['ECE'])} (pass 1; {range_text} {pass_phrase}), "
                "inside the 0.05 line ASSAY-001 used"
            )
        else:
            core = (
                f"On {display}, Snap's chosen-option probabilities measured ECE "
                f"{range_text} {pass_phrase}, inside the 0.05 line ASSAY-001 used"
            )
    elif minimum > 0.05:
        if pass1 is not None:
            direction = pass1["metrics"].get("direction")
            phrases = {
                "over": "overconfident in every bin with at least 50 items",
                "under": "underconfident in every bin with at least 50 items",
                "mixed": "overconfident in some bins and underconfident in others",
                "undetermined": "with direction undetermined under the n ≥ 50 rule",
            }
            core = (
                f"On {display}, Snap's chosen-option probabilities measured ECE "
                f"{_fmt(pass1['metrics']['ECE'])} (pass 1; {range_text} {pass_phrase}), "
                f"outside the 0.05 line ASSAY-001 used, {phrases.get(direction, 'with direction undetermined under the n ≥ 50 rule')}"
            )
        else:
            core = (
                f"On {display}, Snap's chosen-option probabilities measured ECE "
                f"{range_text} {pass_phrase}, outside the 0.05 line ASSAY-001 used; "
                "direction is not stated because pass 1 did not complete"
            )
    else:
        core = (
            f"On {display}, Snap's chosen-option probabilities measured ECE "
            f"{range_text} {pass_phrase}, on both sides of the 0.05 line ASSAY-001 used"
        )

    if pass1 is not None:
        directions = [entry["metrics"].get("direction") for entry in completed]
        if any(direction != directions[0] for direction in directions[1:]):
            core += "; the direction was not the same in every pass"
        interval = pass1["metrics"].get("ECE_ci") or [None, None]
        if interval[0] is not None and interval[1] is not None and interval[0] <= 0.05 <= interval[1]:
            core += f" (pass-1 95% interval {_fmt(interval[0])}–{_fmt(interval[1])} includes 0.05)"
    if k < 3:
        core += f" ({k} of 3 passes completed)"
    return core + "."


def headline(args) -> int:
    wrappers = []
    for raw_path in args.input:
        path = Path(raw_path)
        wrapper = json.load(open(path, encoding="utf-8"))
        if wrapper.get("pass") not in (1, 2, 3):
            raise SystemExit(f"{path} is not a pass score file")
        wrappers.append(wrapper)
    seen = set()
    for wrapper in wrappers:
        key = (wrapper.get("corpus"), wrapper.get("pass"))
        if key in seen:
            raise SystemExit(f"duplicate score input for corpus/pass {key}")
        seen.add(key)

    calibration = {}
    for corpus in DISPLAY_CORPUS:
        entries = [wrapper for wrapper in wrappers if wrapper.get("corpus") == corpus]
        if entries:
            calibration[corpus] = calibration_sentence(corpus, entries)

    n_200 = 0
    violations = 0
    documented = 0
    undocumented = 0
    timestamps = []
    models = set()
    for wrapper in wrappers:
        metrics = wrapper["metrics"]
        n_200 += int(metrics["records"]) - int(metrics["non_200"])
        violations += int(metrics["violations"])
        documented += int(metrics["violations_documented"])
        undocumented += int(metrics["violations_undocumented_only"])
        models.update((metrics.get("models") or {}).keys())
        for key in ("record_ts_min", "record_ts_max"):
            if is_number(wrapper.get(key)):
                timestamps.append(float(wrapper[key]))
    if violations == 0:
        type_sentence = f"Across {n_200} responses there were zero type errors under the checks ASSAY-001 used."
    else:
        type_sentence = (
            f"Across {n_200} responses, {violations} failed the checks ASSAY-001 used: "
            f"{documented} against Snap's documented response shape and {undocumented} only "
            "against checks Snap does not document (probability sum within 0.02, confidence in [0, 1])."
        )

    def timestamp_text(value):
        return datetime.fromtimestamp(value).astimezone().isoformat() if value is not None else "unknown"

    first_call = timestamp_text(min(timestamps)) if timestamps else "unknown"
    last_call = timestamp_text(max(timestamps)) if timestamps else "unknown"
    model_text = ", ".join(f"`{value}`" for value in sorted(models)) or "unknown"
    limit_clause = (
        "A result applies to the artifacts and criteria examined: `subq-snap-preview` "
        f"as served between {first_call} and {last_call} (response `model` values: {model_text}), "
        "Choice questions with null option descriptions in ASSAY-001's option order, these two "
        "corpora, and the docs pages hashed at freeze. It is not a statement about Snap on any "
        "other task, question type, corpus, context length or day."
    )
    output = {
        "scorer": scorer_metadata(),
        "calibration_sentences": calibration,
        "type_error_sentence": type_sentence,
        "accuracy_caveat": (
            "Both corpora are public and old and both appear in Snap's own launch table, "
            "so accuracy is reported, not judged."
        ),
        "limit_clause": limit_clause,
        "travel_together": list(calibration.values()) + [type_sentence, limit_clause],
    }
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(output, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {output_path}")
    else:
        print(json.dumps(output, indent=1))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ASSAY-002 primary scorer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    score_parser = subparsers.add_parser("score", help="score one responses.jsonl")
    score_parser.add_argument("input")
    score_parser.add_argument("labels")
    score_parser.add_argument("--oos", default=None, help="out-of-scope label; defaults to 'oos' if present in labels")
    score_parser.add_argument("--no-oos", action="store_true", help="suppress the automatic OOS readout")
    score_parser.add_argument("--manifest", default=None)
    score_parser.add_argument("--output", default=None)
    score_parser.add_argument("--no-plot", action="store_true")
    score_parser.add_argument("--corpus", default=None)
    score_parser.add_argument("--pass-number", type=int, choices=[1, 2, 3], default=None)
    score_parser.add_argument(
        "--completed",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="override pass completion (default: MANIFEST.json, else true)",
    )

    headline_parser = subparsers.add_parser("headline", help="mechanically build section 7 sentences")
    headline_parser.add_argument("--input", nargs="+", required=True, help="primary score JSON files for passes")
    headline_parser.add_argument("--output", default=None)

    args = parser.parse_args()
    if args.command == "score":
        return score_one(args)
    return headline(args)


if __name__ == "__main__":
    raise SystemExit(main())
