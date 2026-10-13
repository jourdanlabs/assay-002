#!/usr/bin/env python3
import json
import math
import sys
from collections import Counter

import numpy as np


Z95 = 1.959964
BIN_UPPER = [0.1 * i for i in range(1, 11)]
BIN_UPPER_ARRAY = np.asarray(BIN_UPPER, dtype=float)


def is_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def as_object(value):
    return value if isinstance(value, dict) else {}


def path_object(value, *keys):
    current = value
    for key in keys:
        if not isinstance(current, dict):
            return {}
        current = current.get(key)
    return current if isinstance(current, dict) else {}


def status_key(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def ordered_counter(counter):
    def key(item):
        text = str(item[0])
        try:
            return (0, float(text), text)
        except ValueError:
            return (1, 0.0, text)

    return {str(k): int(v) for k, v in sorted(counter.items(), key=key)}


def record_id(record):
    value = record.get("id") if isinstance(record, dict) else None
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def ece_details(values, outcomes):
    values = np.asarray(values, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)
    n_total = len(values)
    if n_total == 0:
        return None, []
    bin_ids = np.minimum(
        9, np.searchsorted(BIN_UPPER_ARRAY, values, side="left")
    )
    counts = np.bincount(bin_ids, minlength=10)
    value_sums = np.bincount(bin_ids, weights=values, minlength=10)
    outcome_sums = np.bincount(bin_ids, weights=outcomes, minlength=10)
    rows = []
    total = 0.0
    for index in range(10):
        count = int(counts[index])
        if count == 0:
            continue
        mean_value = float(value_sums[index] / count)
        accuracy = float(outcome_sums[index] / count)
        gap = mean_value - accuracy
        total += (count / n_total) * abs(gap)
        rows.append(
            {
                "bin": index,
                "n": count,
                "mean_p": mean_value,
                "acc": accuracy,
                "gap": gap,
            }
        )
    return total, rows


def ece10(values, outcomes):
    values = np.asarray(values, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)
    if len(values) == 0:
        return None
    bin_ids = np.minimum(
        9, np.searchsorted(BIN_UPPER_ARRAY, values, side="left")
    )
    counts = np.bincount(bin_ids, minlength=10)
    value_sums = np.bincount(bin_ids, weights=values, minlength=10)
    outcome_sums = np.bincount(bin_ids, weights=outcomes, minlength=10)
    populated = counts > 0
    gaps = np.zeros(10, dtype=float)
    gaps[populated] = (
        value_sums[populated] - outcome_sums[populated]
    ) / counts[populated]
    return float(np.sum((counts / len(values)) * np.abs(gaps)))


def wilson(successes, total):
    if total == 0:
        return None
    phat = successes / total
    z2 = Z95 * Z95
    denominator = 1.0 + z2 / total
    center = (phat + z2 / (2.0 * total)) / denominator
    margin = (
        Z95
        * math.sqrt(
            phat * (1.0 - phat) / total + z2 / (4.0 * total * total)
        )
        / denominator
    )
    return [center - margin, center + margin]


def mean_or_none(values):
    return float(np.mean(values)) if len(values) else None


def percentile_or_none(values, percentile):
    return float(np.percentile(values, percentile)) if len(values) else None


def subset_summary(mask, correct):
    count = int(np.sum(mask))
    successes = int(np.sum(correct[mask])) if count else 0
    return {
        "n": count,
        "share": count / len(correct) if len(correct) else None,
        "acc": successes / count if count else None,
        "wilson": wilson(successes, count),
    }


def average_ranks(values):
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[order[end]] == values[order[start]]:
            end += 1
        average = ((start + 1) + end) / 2.0
        ranks[order[start:end]] = average
        start = end
    return ranks


def round_value(value, digits=4):
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return round(value, digits)
    if isinstance(value, list):
        return [round_value(item, digits) for item in value]
    if isinstance(value, dict):
        return {key: round_value(item, digits) for key, item in value.items()}
    return value


def load_records(path):
    records = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            records.append(json.loads(line))
    return records


def score(records, labels, oos_label=None):
    label_set = set(labels)
    non_200_by_status = Counter()
    attempts = Counter()
    models = Counter()
    input_tokens_sum = 0
    violations = 0
    violations_documented = 0
    violations_undocumented_only = 0
    probability_sums = []
    sum_off_1e3 = 0
    latency = []
    calibration = []

    for raw_record in records:
        record = as_object(raw_record)
        response = as_object(record.get("response"))
        status = response.get("status")
        attempt = response.get("attempt")
        attempts[status_key(attempt)] += 1
        if status != 200:
            non_200_by_status[status_key(status)] += 1
            continue

        body = as_object(response.get("body"))
        model = body.get("model")
        models[status_key(model)] += 1
        usage = as_object(body.get("usage"))
        tokens = usage.get("input_tokens")
        if isinstance(tokens, int) and not isinstance(tokens, bool):
            input_tokens_sum += tokens
        milliseconds = response.get("ms")
        if attempt == 1 and is_number(milliseconds):
            latency.append(float(milliseconds))

        answers = body.get("answers")
        intent_raw = answers.get("intent") if isinstance(answers, dict) else None
        check_a = isinstance(intent_raw, dict)
        intent = intent_raw if check_a else {}
        check_b = intent.get("type") == "choice"
        choice = intent.get("choice")
        check_c = isinstance(choice, str) and choice in label_set
        probabilities_raw = intent.get("probabilities")
        check_d = isinstance(probabilities_raw, dict)
        probabilities = probabilities_raw if check_d else {}
        check_e = check_d and set(probabilities.keys()) == label_set
        check_f = check_d and all(
            is_number(value) and 0.0 <= value <= 1.0
            for value in probabilities.values()
        )
        if check_d and check_f:
            probability_sum = math.fsum(float(v) for v in probabilities.values())
            probability_sums.append(probability_sum)
            if abs(probability_sum - 1.0) > 0.001:
                sum_off_1e3 += 1
        else:
            probability_sum = None
        check_g = (
            check_d
            and check_f
            and abs(probability_sum - 1.0) <= 0.02
        )
        confidence = intent.get("confidence")
        check_h = is_number(confidence) and 0.0 <= confidence <= 1.0
        checks = [check_a, check_b, check_c, check_d, check_e, check_f, check_g, check_h]
        if not all(checks):
            violations += 1
        if not all(checks[:6]):
            violations_documented += 1
        if all(checks[:6]) and (not check_g or not check_h):
            violations_undocumented_only += 1

        p_value = probabilities.get(choice) if check_d else None
        if (
            check_a
            and check_c
            and check_d
            and choice in probabilities
            and is_number(p_value)
            and 0.0 <= p_value <= 1.0
        ):
            calibration.append(
                {
                    "id": record_id(record),
                    "label": record.get("label"),
                    "choice": choice,
                    "probabilities": probabilities,
                    "probabilities_valid": check_f,
                    "p": float(p_value),
                    "correct": int(choice == record.get("label")),
                    "confidence": confidence,
                }
            )

    calibration.sort(key=lambda item: item["id"])
    n_scored = len(calibration)
    p = np.asarray([item["p"] for item in calibration], dtype=float)
    correct = np.asarray([item["correct"] for item in calibration], dtype=int)
    ece, bins = ece_details(p, correct)

    if n_scored:
        mass_order = sorted(
            range(n_scored),
            key=lambda index: (calibration[index]["p"], calibration[index]["id"]),
        )
        equal_mass_ece = 0.0
        for part in np.array_split(np.asarray(mass_order, dtype=int), 10):
            if len(part) == 0:
                continue
            equal_mass_ece += (
                len(part) / n_scored
                * abs(float(np.mean(p[part])) - float(np.mean(correct[part])))
            )
    else:
        equal_mass_ece = None

    brier_rows = []
    for item in calibration:
        row_total = 0.0
        for label in labels:
            value = item["probabilities"].get(label)
            q = float(value) if is_number(value) else 0.0
            y = 1.0 if label == item["label"] else 0.0
            row_total += (q - y) ** 2
        brier_rows.append(row_total)
    brier = mean_or_none(brier_rows)

    large_bins = [row for row in bins if row["n"] >= 50]
    if not large_bins:
        direction = "undetermined"
    elif all(row["gap"] >= 0.0 for row in large_bins):
        direction = "over"
    elif all(row["gap"] <= 0.0 for row in large_bins):
        direction = "under"
    else:
        direction = "mixed"

    if n_scored:
        bootstrap_rng = np.random.default_rng(2002)
        bootstrap = np.empty(2000, dtype=float)
        for index in range(2000):
            sample = bootstrap_rng.integers(0, n_scored, size=n_scored)
            bootstrap[index] = ece10(p[sample], correct[sample])
        ece_ci = [
            float(np.percentile(bootstrap, 2.5)),
            float(np.percentile(bootstrap, 97.5)),
        ]

        noise_rng = np.random.default_rng(2003)
        noise = np.empty(2000, dtype=float)
        for index in range(2000):
            simulated = (noise_rng.random(n_scored) < p).astype(int)
            noise[index] = ece10(p, simulated)
        noise_mean = float(np.mean(noise))
        noise_p95 = float(np.percentile(noise, 95))
    else:
        ece_ci = None
        noise_mean = None
        noise_p95 = None

    gt09_mask = p > 0.9
    ge09_mask = p >= 0.9
    atom1_mask = np.round(p, 6) == 1.0
    gt09 = subset_summary(gt09_mask, correct)
    ge09 = subset_summary(ge09_mask, correct)
    atom1 = subset_summary(atom1_mask, correct)
    gt09_count = int(np.sum(gt09_mask))
    gt09_correct = int(np.sum(correct[gt09_mask])) if gt09_count else 0
    floor = {
        "wrong_all": n_scored - int(np.sum(correct)),
        "wrong_shipped": gt09_count - gt09_correct,
        "right_share_shipped": gt09_correct / gt09_count if gt09_count else None,
        "refused_share": 1.0 - gt09_count / n_scored if n_scored else None,
    }

    argmax_exceptions = 0
    for item in calibration:
        if item["probabilities_valid"]:
            values = [float(value) for value in item["probabilities"].values()]
            if values and item["p"] < max(values) - 1e-9:
                argmax_exceptions += 1

    confidence_rows = []
    for item in calibration:
        confidence = item["confidence"]
        if is_number(confidence) and 0.0 <= confidence <= 1.0:
            confidence_rows.append(
                (float(confidence), item["id"], item["correct"], item)
            )
    confidence_rows.sort(key=lambda item: (item[0], item[1]))
    confidence_values = np.asarray([item[0] for item in confidence_rows], dtype=float)
    confidence_correct = np.asarray([item[2] for item in confidence_rows], dtype=int)
    conf_deciles = []
    for part in np.array_split(np.arange(len(confidence_rows), dtype=int), 10):
        if len(part) == 0:
            continue
        conf_deciles.append(
            {
                "n": int(len(part)),
                "mean_confidence": float(np.mean(confidence_values[part])),
                "accuracy": float(np.mean(confidence_correct[part])),
            }
        )
    conf_monotone = all(
        conf_deciles[index]["accuracy"] >= conf_deciles[index - 1]["accuracy"]
        for index in range(1, len(conf_deciles))
    )
    ece_conf = ece10(confidence_values, confidence_correct)
    conf_atom1_share = (
        float(np.mean(np.round(confidence_values, 6) == 1.0))
        if len(confidence_values)
        else None
    )

    oos = None
    if oos_label is not None:
        oos_mask = np.asarray(
            [item["label"] == oos_label for item in calibration], dtype=bool
        )
        inscope_mask = ~oos_mask
        n_oos = int(np.sum(oos_mask))
        n_inscope = int(np.sum(inscope_mask))

        oos_confidence = [
            float(item["confidence"])
            for item in calibration
            if item["label"] == oos_label
            and is_number(item["confidence"])
            and 0.0 <= item["confidence"] <= 1.0
        ]
        inscope_confidence = [
            float(item["confidence"])
            for item in calibration
            if item["label"] != oos_label
            and is_number(item["confidence"])
            and 0.0 <= item["confidence"] <= 1.0
        ]
        if n_oos and n_inscope:
            ranks = average_ranks(p)
            rank_sum = float(np.sum(ranks[inscope_mask]))
            auroc = (
                rank_sum - n_inscope * (n_inscope + 1) / 2.0
            ) / (n_inscope * n_oos)
        else:
            auroc = None
        oos = {
            "n_oos": n_oos,
            "n_inscope": n_inscope,
            "acc_oos": mean_or_none(correct[oos_mask]),
            "acc_inscope": mean_or_none(correct[inscope_mask]),
            "mean_p_oos": mean_or_none(p[oos_mask]),
            "mean_p_inscope": mean_or_none(p[inscope_mask]),
            "mean_conf_oos": mean_or_none(oos_confidence),
            "mean_conf_inscope": mean_or_none(inscope_confidence),
            "high_p_wrong_oos": (
                int(np.sum(oos_mask & (correct == 0) & (p > 0.9))) / n_oos
                if n_oos
                else None
            ),
            "AUROC": auroc,
        }

    output = {
        "records": len(records),
        "non_200": sum(non_200_by_status.values()),
        "non_200_by_status": ordered_counter(non_200_by_status),
        "scored": n_scored,
        "violations": violations,
        "violations_documented": violations_documented,
        "violations_undocumented_only": violations_undocumented_only,
        "sum_min": min(probability_sums) if probability_sums else None,
        "sum_max": max(probability_sums) if probability_sums else None,
        "sum_off_1e3": sum_off_1e3,
        "accuracy": mean_or_none(correct),
        "mean_p": mean_or_none(p),
        "signed_gap": (
            mean_or_none(p) - mean_or_none(correct) if n_scored else None
        ),
        "ECE": ece,
        "ECE_ci": ece_ci,
        "noise_mean": noise_mean,
        "noise_p95": noise_p95,
        "ECE_equal_mass": equal_mass_ece,
        "MCE_all": max((abs(row["gap"]) for row in bins), default=None),
        "MCE_50": max((abs(row["gap"]) for row in large_bins), default=None),
        "Brier": brier,
        "direction": direction,
        "bins": bins,
        "gt09": gt09,
        "ge09": ge09,
        "atom1": atom1,
        "floor": floor,
        "argmax_exceptions": argmax_exceptions,
        "latency_median": round(percentile_or_none(latency, 50), 1)
        if latency
        else None,
        "latency_p95": round(percentile_or_none(latency, 95), 1)
        if latency
        else None,
        "latency_p99": round(percentile_or_none(latency, 99), 1)
        if latency
        else None,
        "attempts": ordered_counter(attempts),
        "models": ordered_counter(models),
        "input_tokens_sum": input_tokens_sum,
        "conf_deciles": conf_deciles,
        "conf_monotone": conf_monotone,
        "ECE_conf": ece_conf,
        "conf_atom1_share": conf_atom1_share,
        "oos": oos,
    }
    latency_keys = {"latency_median", "latency_p95", "latency_p99"}
    return {
        key: value if key in latency_keys else round_value(value)
        for key, value in output.items()
    }


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit("usage: rescore.py responses.jsonl labels.json [oos-label]")
    records = load_records(sys.argv[1])
    with open(sys.argv[2], "r", encoding="utf-8") as handle:
        labels = json.load(handle)
    result = score(records, labels, sys.argv[3] if len(sys.argv) == 4 else None)
    print(json.dumps(result, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
