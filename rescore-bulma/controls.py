#!/usr/bin/env python3
import hashlib
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path


CORPORA = {
    "banking77": ("b77", 3080, "banking77.json"),
    "clinc150": ("c150", 5500, "clinc150.json"),
}


def record(item_id, gold, choice, probabilities, confidence, tag="control"):
    return {
        "id": item_id,
        "label": gold,
        "tag": tag,
        "response": {
            "status": 200,
            "ms": 10.0,
            "attempt": 1,
            "body": {
                "model": "positive-control",
                "answers": {
                    "intent": {
                        "type": "choice",
                        "choice": choice,
                        "probabilities": probabilities,
                        "confidence": confidence,
                    }
                },
                "usage": {"input_tokens": 1, "output_tokens": 0},
            },
        },
    }


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")


def synthetic_rows(labels, prefix, count, mode, seed=1):
    rng = random.Random(seed)
    k = len(labels)
    uniform = {label: 1.0 / k for label in labels}
    for index in range(count):
        gold = labels[index % k]
        if mode == "uniform":
            choice = labels[rng.randrange(k)]
            probabilities = dict(uniform)
            confidence = 1.0 / k
        elif mode == "overconfident":
            choice = labels[rng.randrange(k)]
            probabilities = {label: 0.0 for label in labels}
            probabilities[choice] = 1.0
            confidence = 1.0
        elif mode == "perfect":
            choice = gold
            probabilities = {label: 0.0 for label in labels}
            probabilities[choice] = 1.0
            confidence = 1.0
        else:
            raise ValueError(mode)
        yield record(
            f"{prefix}-{index:04d}",
            gold,
            choice,
            probabilities,
            confidence,
        )


def run_json(command):
    completed = subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return json.loads(completed.stdout), completed.stdout.encode("utf-8")


def score(script, data_path, labels_path):
    return run_json([sys.executable, str(script), str(data_path), str(labels_path)])


def broken_rows(labels):
    def good(index):
        gold = labels[index % len(labels)]
        probabilities = {label: 0.0 for label in labels}
        probabilities[gold] = 1.0
        return record(
            f"broken-{index:02d}", gold, gold, probabilities, 1.0
        )

    rows = [good(index) for index in range(8)]
    del rows[0]["response"]["body"]["answers"]["intent"]
    rows[1]["response"]["body"]["answers"]["intent"]["type"] = "score"
    rows[2]["response"]["body"]["answers"]["intent"]["choice"] = "not-a-label"
    rows[3]["response"]["body"]["answers"]["intent"]["probabilities"] = []
    probabilities = rows[4]["response"]["body"]["answers"]["intent"]["probabilities"]
    del probabilities[next(label for label, value in probabilities.items() if value == 0)]
    rows[5]["response"]["body"]["answers"]["intent"]["probabilities"][labels[1]] = "bad"
    probabilities = rows[6]["response"]["body"]["answers"]["intent"]["probabilities"]
    probabilities[rows[6]["label"]] = 0.5
    rows[7]["response"]["body"]["answers"]["intent"]["confidence"] = 2.0
    return rows


def rounded_rows(labels):
    rows = []
    for index in range(20):
        gold = labels[index % len(labels)]
        probabilities = {label: 0.0 for label in labels}
        probabilities[gold] = 0.99 if index % 2 == 0 else 1.0
        rows.append(
            record(
                f"rounded-{index:02d}",
                gold,
                gold,
                probabilities,
                probabilities[gold],
            )
        )
    return rows


def pair_rows(labels, count):
    original = []
    mutated = []
    flips = 7
    for index in range(count):
        gold = labels[index % len(labels)]
        probabilities = {label: 0.0 for label in labels}
        probabilities[gold] = 1.0
        original.append(
            record(f"pair-{index:03d}", gold, gold, dict(probabilities), 1.0)
        )
        if index < flips:
            changed = labels[(index + 1) % len(labels)]
            changed_probabilities = {label: 0.0 for label in labels}
            changed_probabilities[changed] = 1.0
            mutated.append(
                record(
                    f"pair-{index:03d}",
                    gold,
                    changed,
                    changed_probabilities,
                    1.0,
                )
            )
        else:
            mutated.append(
                record(f"pair-{index:03d}", gold, gold, dict(probabilities), 1.0)
            )
    return original, mutated, flips


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    here = Path(__file__).resolve().parent
    root = here.parent
    labels_root = root / "labels"
    scorer = here / "rescore.py"
    pair_scorer = here / "pairs.py"
    report = {"seed": 1, "corpora": {}, "checks": {}}

    with tempfile.TemporaryDirectory(prefix="bulma-assay-controls-") as temp:
        temp_root = Path(temp)
        saved_perfect = {}
        saved_uniform = {}
        for corpus, (prefix, count, labels_name) in CORPORA.items():
            labels_path = labels_root / labels_name
            labels = json.loads(labels_path.read_text(encoding="utf-8"))
            corpus_result = {
                "n": count,
                "k": len(labels),
            }
            for mode in ("uniform", "overconfident", "perfect"):
                data_path = temp_root / f"{corpus}-{mode}.jsonl"
                write_jsonl(
                    data_path,
                    synthetic_rows(labels, prefix, count, mode, seed=1),
                )
                result, raw_output = score(scorer, data_path, labels_path)
                corpus_result[mode] = {
                    "records": result["records"],
                    "scored": result["scored"],
                    "accuracy": result["accuracy"],
                    "ECE": result["ECE"],
                    "output_sha256": hashlib.sha256(raw_output).hexdigest(),
                }
                require(
                    result["records"] == count and result["scored"] == count,
                    f"{corpus} {mode}: incomplete coverage",
                )
                if mode == "uniform":
                    require(result["ECE"] <= 0.03, f"{corpus}: uniform ECE")
                    require(
                        abs(result["accuracy"] - 1.0 / len(labels)) <= 0.03,
                        f"{corpus}: uniform accuracy",
                    )
                    saved_uniform[corpus] = (data_path, labels_path, raw_output, result)
                elif mode == "overconfident":
                    require(result["ECE"] >= 0.9, f"{corpus}: overconfident ECE")
                else:
                    require(
                        result["ECE"] == 0.0 and result["accuracy"] == 1.0,
                        f"{corpus}: perfect oracle",
                    )
                    saved_perfect[corpus] = (data_path, labels_path, raw_output, result)
            report["corpora"][corpus] = corpus_result

        banking_labels_path = labels_root / CORPORA["banking77"][2]
        banking_labels = json.loads(banking_labels_path.read_text(encoding="utf-8"))

        broken_path = temp_root / "broken.jsonl"
        write_jsonl(broken_path, broken_rows(banking_labels))
        broken_result, _ = score(scorer, broken_path, banking_labels_path)
        require(broken_result["violations"] == 8, "broken: total violations")
        require(
            broken_result["violations_documented"] == 6,
            "broken: documented violations",
        )
        require(
            broken_result["violations_undocumented_only"] == 2,
            "broken: undocumented-only violations",
        )
        report["checks"]["broken_schema"] = {
            "injected": 8,
            "caught": broken_result["violations"],
            "documented": broken_result["violations_documented"],
            "undocumented_only": broken_result["violations_undocumented_only"],
        }

        rounded_path = temp_root / "rounded.jsonl"
        write_jsonl(rounded_path, rounded_rows(banking_labels))
        rounded_result, _ = score(scorer, rounded_path, banking_labels_path)
        require(rounded_result["records"] == 20, "rounded: records")
        require(rounded_result["scored"] == 20, "rounded: calibration n")
        require(rounded_result["sum_off_1e3"] == 10, "rounded: 1e-3 count")
        require(rounded_result["violations"] == 0, "rounded: 0.02 tolerance")
        report["checks"]["rounded_sums"] = {
            "records": rounded_result["records"],
            "scored": rounded_result["scored"],
            "sum_off_1e3": rounded_result["sum_off_1e3"],
            "violations": rounded_result["violations"],
        }

        perfect_path, perfect_labels, perfect_raw, perfect_result = saved_perfect[
            "banking77"
        ]
        shuffled_path = temp_root / "perfect-shuffled.jsonl"
        lines = perfect_path.read_text(encoding="utf-8").splitlines()
        random.Random(1).shuffle(lines)
        shuffled_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        shuffled_result, shuffled_raw = score(scorer, shuffled_path, perfect_labels)
        require(perfect_result == shuffled_result, "shuffle invariance")
        report["checks"]["shuffle_invariance"] = {
            "equal": True,
            "original_sha256": hashlib.sha256(perfect_raw).hexdigest(),
            "shuffled_sha256": hashlib.sha256(shuffled_raw).hexdigest(),
        }

        pair_original, pair_mutated, expected_flips = pair_rows(banking_labels, 100)
        pair_a = temp_root / "pairs-a.jsonl"
        pair_b = temp_root / "pairs-b.jsonl"
        write_jsonl(pair_a, pair_original)
        write_jsonl(pair_b, pair_mutated)
        self_result, _ = run_json(
            [sys.executable, str(pair_scorer), str(pair_a), str(pair_a)]
        )
        mutated_result, _ = run_json(
            [sys.executable, str(pair_scorer), str(pair_a), str(pair_b)]
        )
        require(self_result["flips"] == 0, "pairs self")
        require(mutated_result["flips"] == expected_flips, "pairs mutated")
        report["checks"]["pairs"] = {
            "self_flips": self_result["flips"],
            "mutated_flips": mutated_result["flips"],
            "expected_mutated_flips": expected_flips,
        }

        uniform_path, uniform_labels, uniform_raw, uniform_result = saved_uniform[
            "clinc150"
        ]
        repeated_result, repeated_raw = score(scorer, uniform_path, uniform_labels)
        require(uniform_result["ECE_ci"] == repeated_result["ECE_ci"], "seed ECE_ci")
        require(
            uniform_result["noise_mean"] == repeated_result["noise_mean"],
            "seed noise_mean",
        )
        require(
            uniform_result["noise_p95"] == repeated_result["noise_p95"],
            "seed noise_p95",
        )
        require(uniform_raw == repeated_raw, "seed full output")
        report["checks"]["seed_determinism"] = {
            "equal": True,
            "output_sha256": hashlib.sha256(repeated_raw).hexdigest(),
            "ECE_ci": repeated_result["ECE_ci"],
            "noise_mean": repeated_result["noise_mean"],
            "noise_p95": repeated_result["noise_p95"],
        }

    report["status"] = "PASS"
    print(json.dumps(report, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
