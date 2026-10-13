#!/usr/bin/env python3
"""ASSAY-002 positive controls.

Synthetic records cover every corpus item with seed 1 and are scored by the
final primary scorer before any Snap output is scored. If any registered
expectation misses, this program exits nonzero and nothing should be scored.
"""
from __future__ import annotations

import copy
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from run import load_corpus, make_request  # noqa: E402
from score import analyze_records, load_records, scorer_metadata  # noqa: E402
from pairs import compute_pairs  # noqa: E402

SEED = 1
PAIR_MUTATIONS = 17
MODES = ["uniform-random", "overconfident", "perfect-oracle", "broken-schema", "rounded-sums"]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def synth(corpus: str, mode: str, seed: int = SEED):
    items, labels = load_corpus(corpus)
    k = len(labels)
    rng = random.Random(seed)
    outdir = ROOT / "controls" / corpus
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{mode}.jsonl"
    injected_breaks = []
    designated_rounded = []

    with open(path, "w", encoding="utf-8") as handle:
        for index, item in enumerate(items):
            request = make_request(corpus, item, labels)
            if mode in ("perfect-oracle", "rounded-sums"):
                choice = item["label"]
            else:
                choice = rng.choice(labels)

            if mode in ("uniform-random", "broken-schema"):
                probabilities = {label: 1.0 / k for label in labels}
                confidence = 1.0 / k
                if mode == "broken-schema" and rng.random() < 0.01:
                    dropped = rng.choice([label for label in labels if label != choice])
                    probabilities.pop(dropped)
                    injected_breaks.append(item["id"])
            elif mode == "rounded-sums":
                probabilities = {label: 0.0 for label in labels}
                if index % 10 == 0:
                    # 0.994 plus two 0.003 values rounds to 0.99 at 2 dp.
                    probabilities[choice] = 0.99
                    designated_rounded.append(item["id"])
                else:
                    probabilities[choice] = 1.0
                confidence = probabilities[choice]
            else:
                probabilities = {label: (1.0 if label == choice else 0.0) for label in labels}
                confidence = 1.0

            response = {
                "status": 200,
                "ms": 100.0,
                "attempt": 1,
                "retries": [],
                "body": {
                    "model": "control",
                    "answers": {
                        "intent": {
                            "type": "choice",
                            "choice": choice,
                            "probabilities": probabilities,
                            "confidence": confidence,
                        }
                    },
                    "usage": {"input_tokens": 0, "output_tokens": 0},
                },
            }
            record = {
                "id": item["id"],
                "label": item["label"],
                "request": request,
                "response": response,
                "ts": 0,
            }
            handle.write(json.dumps(record) + "\n")

    return path, {
        "records": len(items),
        "injected_break_ids": injected_breaks,
        "injected_breaks": len(injected_breaks),
        "designated_rounded_ids": designated_rounded,
        "designated_rounded": len(designated_rounded),
    }


def add_check(checks, corpus, control, name, condition, expected, observed):
    checks.append(
        {
            "corpus": corpus,
            "control": control,
            "check": name,
            "expected": expected,
            "observed": observed,
            "pass": bool(condition),
        }
    )


def score_with_cli(corpus: str, mode: str, input_path: Path):
    output_path = ROOT / "controls" / "scores" / f"control-{mode}-{corpus}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(ROOT / "harness" / "score.py"),
        "score",
        str(input_path.relative_to(ROOT)),
        f"labels/{corpus}.json",
        "--output",
        str(output_path.relative_to(ROOT)),
        "--no-plot",
        "--corpus",
        corpus,
    ]
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    return output_path, json.load(open(output_path, encoding="utf-8"))


def run_pairs_cli(corpus: str, name: str, path_a: Path, path_b: Path):
    output_path = ROOT / "controls" / "scores" / f"control-pairs-{name}-{corpus}.json"
    command = [
        sys.executable,
        str(ROOT / "harness" / "pairs.py"),
        str(path_a.relative_to(ROOT)),
        str(path_b.relative_to(ROOT)),
        "--labels",
        f"labels/{corpus}.json",
        "--output",
        str(output_path.relative_to(ROOT)),
    ]
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    return output_path, json.load(open(output_path, encoding="utf-8"))


def mutate_pairs_file(corpus: str, source: Path, labels):
    records = load_records(source)
    selected_ids = sorted(record["id"] for record in records)[:PAIR_MUTATIONS]
    mutated = copy.deepcopy(records)
    label_index = {label: index for index, label in enumerate(labels)}
    for record in mutated:
        if record["id"] not in selected_ids:
            continue
        intent = record["response"]["body"]["answers"]["intent"]
        old_choice = intent["choice"]
        new_choice = labels[(label_index[old_choice] + 1) % len(labels)]
        intent["choice"] = new_choice
        intent["probabilities"] = {
            label: (1.0 if label == new_choice else 0.0) for label in labels
        }
        intent["confidence"] = 1.0
    out_path = ROOT / "controls" / corpus / f"pairs-mutated-{PAIR_MUTATIONS}.jsonl"
    with open(out_path, "w", encoding="utf-8") as handle:
        for record in mutated:
            handle.write(json.dumps(record) + "\n")
    return out_path, selected_ids


def main() -> int:
    checks = []
    generated = {}
    score_outputs = {}
    pair_outputs = {}

    for corpus in ("banking77", "clinc150"):
        _items, labels = load_corpus(corpus)
        k = len(labels)
        n = _items and len(_items)
        generated[corpus] = {}
        score_outputs[corpus] = {}
        uniforms_for_direct = None

        for mode in MODES:
            path, metadata = synth(corpus, mode)
            generated[corpus][mode] = {
                "path": str(path.relative_to(ROOT)),
                "sha256": file_sha256(path),
                **metadata,
            }
            score_path, scored = score_with_cli(corpus, mode, path)
            score_outputs[corpus][mode] = str(score_path.relative_to(ROOT))
            metrics = scored["metrics"]
            print(
                f"{corpus:10s} {mode:16s} scored={metrics['scored']:5d} "
                f"acc={metrics['accuracy']} ECE={metrics['ECE']} violations={metrics['violations']}",
                flush=True,
            )

            add_check(checks, corpus, mode, "scored", metrics["scored"] == n, n, metrics["scored"])
            if mode == "uniform-random":
                uniforms_for_direct = path
                add_check(checks, corpus, mode, "violations", metrics["violations"] == 0, 0, metrics["violations"])
                add_check(
                    checks, corpus, mode, "accuracy_approx_1_over_K",
                    abs(metrics["accuracy"] - 1.0 / k) <= 0.005,
                    f"within 0.005 of {1.0 / k:.6f}", metrics["accuracy"],
                )
                add_check(checks, corpus, mode, "ECE_approx_0", metrics["ECE"] <= 0.005, "<= 0.005", metrics["ECE"])
            elif mode == "overconfident":
                add_check(checks, corpus, mode, "violations", metrics["violations"] == 0, 0, metrics["violations"])
                add_check(
                    checks, corpus, mode, "ECE_approx_1_minus_1_over_K",
                    abs(metrics["ECE"] - (1.0 - 1.0 / k)) <= 0.005,
                    f"within 0.005 of {1.0 - 1.0 / k:.6f}", metrics["ECE"],
                )
            elif mode == "perfect-oracle":
                add_check(checks, corpus, mode, "violations", metrics["violations"] == 0, 0, metrics["violations"])
                add_check(checks, corpus, mode, "accuracy", metrics["accuracy"] == 1.0, 1.0, metrics["accuracy"])
                add_check(checks, corpus, mode, "ECE", metrics["ECE"] == 0.0, 0.0, metrics["ECE"])
            elif mode == "broken-schema":
                injected = metadata["injected_breaks"]
                add_check(checks, corpus, mode, "injected_positive", injected > 0, "> 0", injected)
                add_check(
                    checks, corpus, mode, "violations_exact",
                    metrics["violations"] == injected,
                    injected, metrics["violations"],
                )
                add_check(
                    checks, corpus, mode, "documented_exact",
                    metrics["violations_documented"] == injected,
                    injected, metrics["violations_documented"],
                )
                add_check(
                    checks, corpus, mode, "undocumented_only",
                    metrics["violations_undocumented_only"] == 0,
                    0, metrics["violations_undocumented_only"],
                )
            elif mode == "rounded-sums":
                designated = metadata["designated_rounded"]
                add_check(checks, corpus, mode, "violations_at_0.02", metrics["violations"] == 0, 0, metrics["violations"])
                add_check(
                    checks, corpus, mode, "sum_off_1e3_exact",
                    metrics["sum_off_1e3"] == designated,
                    designated, metrics["sum_off_1e3"],
                )
                add_check(
                    checks, corpus, mode, "calibration_n_unchanged",
                    metrics["scored"] == n, n, metrics["scored"],
                )
                add_check(checks, corpus, mode, "accuracy", metrics["accuracy"] == 1.0, 1.0, metrics["accuracy"])

        # Direct-function controls. The primary analyzer sorts calibration IDs,
        # so record order and RNG seeding must not move any metric.
        uniform_records = load_records(uniforms_for_direct)
        oos_label = "oos" if "oos" in labels else None
        direct_one = analyze_records(uniform_records, labels, oos_label=oos_label)["metrics"]
        direct_two = analyze_records(uniform_records, labels, oos_label=oos_label)["metrics"]
        add_check(
            checks, corpus, "seed-determinism", "bootstrap_and_noise_identical",
            direct_one["ECE_ci"] == direct_two["ECE_ci"]
            and direct_one["noise_mean"] == direct_two["noise_mean"]
            and direct_one["noise_p95"] == direct_two["noise_p95"],
            "identical ECE_ci, noise_mean and noise_p95 on two runs",
            {
                "run1": [direct_one["ECE_ci"], direct_one["noise_mean"], direct_one["noise_p95"]],
                "run2": [direct_two["ECE_ci"], direct_two["noise_mean"], direct_two["noise_p95"]],
            },
        )
        shuffled_records = list(uniform_records)
        random.Random(SEED).shuffle(shuffled_records)
        shuffled_metrics = analyze_records(shuffled_records, labels, oos_label=oos_label)["metrics"]
        add_check(
            checks, corpus, "shuffle-invariance", "metrics_identical",
            json.dumps(direct_one, sort_keys=True) == json.dumps(shuffled_metrics, sort_keys=True),
            "identical metric JSON after shuffling record order",
            "identical" if direct_one == shuffled_metrics else "different",
        )

        perfect_path = ROOT / generated[corpus]["perfect-oracle"]["path"]
        mutated_path, mutated_ids = mutate_pairs_file(corpus, perfect_path, labels)
        generated[corpus]["pairs-mutated"] = {
            "path": str(mutated_path.relative_to(ROOT)),
            "sha256": file_sha256(mutated_path),
            "records": n,
            "mutated_ids": mutated_ids,
            "mutations": PAIR_MUTATIONS,
        }
        pair_outputs[corpus] = {}
        self_path, self_result = run_pairs_cli(corpus, "self", perfect_path, perfect_path)
        changed_path, changed_result = run_pairs_cli(corpus, "mutated", perfect_path, mutated_path)
        pair_outputs[corpus]["self"] = str(self_path.relative_to(ROOT))
        pair_outputs[corpus]["mutated"] = str(changed_path.relative_to(ROOT))
        add_check(
            checks, corpus, "pairs", "self_flips",
            self_result["metrics"]["flips"] == 0, 0, self_result["metrics"]["flips"],
        )
        add_check(
            checks, corpus, "pairs", "mutated_flips_exact",
            changed_result["metrics"]["flips"] == PAIR_MUTATIONS,
            PAIR_MUTATIONS, changed_result["metrics"]["flips"],
        )
        # The import-level path must agree with the CLI path.
        direct_pairs = compute_pairs(load_records(perfect_path), load_records(mutated_path), labels)
        add_check(
            checks, corpus, "pairs", "direct_matches_cli",
            direct_pairs["metrics"] == changed_result["metrics"],
            "identical pairs metrics", "identical" if direct_pairs["metrics"] == changed_result["metrics"] else "different",
        )

    result = {
        "scorer": scorer_metadata(),
        "pairs_scorer_sha256": file_sha256(ROOT / "harness" / "pairs.py"),
        "seed": SEED,
        "pair_mutations_per_corpus": PAIR_MUTATIONS,
        "generated": generated,
        "score_outputs": score_outputs,
        "pair_outputs": pair_outputs,
        "checks": checks,
        "all_pass": all(check["pass"] for check in checks),
    }
    result_path = ROOT / "controls" / "CONTROL-RESULTS.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(f"controls: {'PASS' if result['all_pass'] else 'FAIL'} -> {result_path}")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
