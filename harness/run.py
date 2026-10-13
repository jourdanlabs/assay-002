#!/usr/bin/env python3
"""ASSAY-002 — SubQ Snap calibration runner.

The scientific design is frozen in PROTOCOL.md. This file only executes the
registered steps; it does not choose samples, metrics or thresholds at run
time. The API key is read from ~/.config/subq/api_key and is never printed,
logged or written. Request records contain bodies only, never headers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
API_URL = "https://api.subq.ai/v1/systemone"
MODELS_URL = "https://api.subq.ai/v1/models"
API = API_URL  # assay-001 compatibility for imported helpers
MODEL = "subq-snap-preview"
USER_AGENT = "ASSAY-002/1.0"
KEY_PATH = Path.home() / ".config" / "subq" / "api_key"
CAP_TOKENS = 60_000_000
TIMEOUT_S = 60
CLINC_FULL_TIMEOUT_S = 120
PLANNED_CALLS = {"banking77": 9_993, "clinc150": 16_603}
EXPECTED_COUNTS = {"banking77": (3_080, 77), "clinc150": (5_500, 151)}

INSTRUCTIONS = {
    "banking77": "Which banking intent does this customer message express? Choose exactly one.",
    "clinc150": "Which intent does this user request express? Choose exactly one. Choose oos if it matches none of the others.",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def machine_now() -> str:
    return datetime.now().astimezone().isoformat()


def read_hash_manifest(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing hash manifest: {path}")
    entries = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, filename = line.split(None, 1)
        entries[filename.lstrip("*")] = digest
    return entries


def verify_hash_manifest(path: Path) -> dict:
    entries = read_hash_manifest(path)
    failures = []
    for filename, expected in entries.items():
        candidate = ROOT / filename
        if not candidate.exists():
            failures.append(f"missing {filename}")
        elif sha256_file(candidate) != expected:
            failures.append(f"hash mismatch {filename}")
    if failures:
        raise SystemExit("freeze verification failed: " + "; ".join(failures))
    return entries


def load_freeze() -> dict:
    freeze_path = ROOT / "FREEZE.sha256"
    entries = verify_hash_manifest(freeze_path)
    verify_hash_manifest(ROOT / "CORPUS.sha256")
    verify_hash_manifest(ROOT / "DOCS.sha256")
    protocol_sha = entries.get("PROTOCOL.md")
    if not protocol_sha:
        raise SystemExit("FREEZE.sha256 has no PROTOCOL.md entry")
    return {
        "entries": entries,
        "freeze_sha256": sha256_file(freeze_path),
        "protocol_sha256": protocol_sha,
    }


def git_head():
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def load_key() -> str:
    try:
        key = KEY_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise SystemExit("no API key file at ~/.config/subq/api_key")
    if not key:
        raise SystemExit("API key file at ~/.config/subq/api_key is empty")
    return key


def load_labels(name: str):
    labels = json.load(open(ROOT / "labels" / f"{name}.json", encoding="utf-8"))
    if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
        raise SystemExit(f"labels/{name}.json is not a list of strings")
    if len(labels) != len(set(labels)):
        raise SystemExit(f"labels/{name}.json contains duplicates")
    return labels


def load_corpus(name: str):
    labels = load_labels(name)
    if name == "banking77":
        frame = pd.read_csv(ROOT / "corpus/banking77/test.csv")
        items = [
            {"id": f"b77-{i:04d}", "text": str(row.text), "label": str(row.category)}
            for i, row in enumerate(frame.itertuples())
        ]
    elif name == "clinc150":
        frame = pd.read_parquet(ROOT / "corpus/clinc150/test.parquet")
        items = [
            {"id": f"c150-{i:04d}", "text": str(row.text), "label": labels[int(row.intent)]}
            for i, row in enumerate(frame.itertuples())
        ]
    else:
        raise SystemExit(f"unknown corpus: {name}")
    expected_items, expected_labels = EXPECTED_COUNTS[name]
    if len(items) != expected_items or len(labels) != expected_labels:
        raise SystemExit(
            f"corpus shape mismatch for {name}: {len(items)} items, {len(labels)} labels"
        )
    if not all(item["label"] in labels for item in items):
        raise SystemExit(f"a gold label for {name} is outside labels/{name}.json")
    return items, labels


def load_permutations(labels):
    data = json.load(open(ROOT / "labels/b77-permutations-300.json", encoding="utf-8"))
    if data.get("seed") != 20260920 or data.get("n") != 300:
        raise SystemExit("permutations file has the wrong seed or count")
    items = data.get("items")
    if not isinstance(items, list) or len(items) != 300:
        raise SystemExit("permutations file does not hold 300 items")
    by_id = {}
    for entry in items:
        options = entry.get("options")
        if not isinstance(options, list) or sorted(options) != sorted(labels):
            raise SystemExit("a frozen permutation is not a permutation of the labels")
        by_id[entry.get("id")] = options
    return by_id


def make_request(name, item, labels, options=None):
    ordered = list(labels if options is None else options)
    return {
        "state": item["text"],
        "model": MODEL,
        "questions": {
            "intent": {
                "type": "choice",
                "instructions": INSTRUCTIONS[name],
                "criteria": {label: None for label in ordered},
            }
        },
    }


class RunControl:
    def __init__(self):
        self.stop_event = threading.Event()
        self._lock = threading.Lock()
        self.stop_reason = None

    def request_stop(self, reason: str):
        with self._lock:
            if self.stop_reason is None:
                self.stop_reason = reason
            self.stop_event.set()


class ConcurrencyGate:
    def __init__(self, limit: int, control: RunControl):
        self.limit = limit
        self.control = control
        self._condition = threading.Condition()
        self._active = 0
        self._paused_until = 0.0

    def acquire(self) -> bool:
        with self._condition:
            while True:
                if self.control.stop_event.is_set():
                    return False
                now = time.monotonic()
                if now < self._paused_until:
                    self._condition.wait(min(0.25, self._paused_until - now))
                    continue
                if self._active < self.limit:
                    self._active += 1
                    return True
                self._condition.wait(0.25)

    def release(self):
        with self._condition:
            self._active -= 1
            self._condition.notify_all()

    def trip(self):
        with self._condition:
            before = self.limit
            self.limit = max(1, self.limit // 2)
            self._paused_until = time.monotonic() + 60
            self._condition.notify_all()
            return before, self.limit


class CapMeter:
    def __init__(self, total_tokens: int, max_seen: int, cap_tokens: int = CAP_TOKENS):
        self.cap_tokens = cap_tokens
        self.total_tokens = int(total_tokens)
        self.max_seen = int(max_seen)
        self.step_tokens = 0
        self._reserved = 0
        self._lock = threading.Lock()
        self.stopped = self.total_tokens >= cap_tokens

    def admit(self):
        with self._lock:
            if self.stopped:
                return None
            estimate = self.max_seen
            if self.total_tokens + self._reserved + estimate > self.cap_tokens:
                self.stopped = True
                return None
            self._reserved += estimate
            return estimate

    def finish(self, estimate: int, actual_tokens: int):
        with self._lock:
            self._reserved -= estimate
            actual = max(0, int(actual_tokens or 0))
            self.total_tokens += actual
            self.step_tokens += actual
            self.max_seen = max(self.max_seen, actual)
            if self.total_tokens >= self.cap_tokens:
                self.stopped = True


def retry_after_seconds(value):
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        pass
    try:
        moment = parsedate_to_datetime(value)
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return max(0.0, moment.timestamp() - time.time())
    except Exception:
        return None


def post(key, body, timeout=TIMEOUT_S, max_tries=8, sleep=time.sleep):
    data = json.dumps(body).encode()
    retries = []
    delay = 1.0
    for attempt in range(1, max_tries + 1):
        request = urllib.request.Request(
            API_URL,
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
                result = {
                    "status": int(response.status),
                    "ms": round((time.perf_counter() - started) * 1000, 1),
                    "attempt": attempt,
                    "retries": list(retries),
                }
                try:
                    result["body"] = json.loads(raw)
                except Exception:
                    result["error"] = raw.decode(errors="replace")[:2000]
                return result
        except urllib.error.HTTPError as exc:
            ms = round((time.perf_counter() - started) * 1000, 1)
            text = exc.read().decode(errors="replace")
            status = int(exc.code)
            if (status == 429 or 500 <= status <= 599) and attempt < max_tries:
                retries.append(status)
                wait = delay
                header = retry_after_seconds(exc.headers.get("Retry-After") if exc.headers else None)
                if header is not None:
                    wait = max(wait, header)
                sleep(wait)
                delay = min(delay * 2, 30.0)
                continue
            return {
                "status": status,
                "ms": ms,
                "attempt": attempt,
                "retries": list(retries),
                "error": text[:2000],
            }
        except Exception as exc:  # network error or timeout: registered as no retry
            return {
                "status": 0,
                "ms": round((time.perf_counter() - started) * 1000, 1),
                "attempt": attempt,
                "retries": list(retries),
                "error": repr(exc)[:2000],
            }
    raise AssertionError("post retry loop fell through")


def usage_input_tokens(response):
    if not isinstance(response, dict) or response.get("status") != 200:
        return 0
    body = response.get("body")
    if not isinstance(body, dict):
        return 0
    usage = body.get("usage")
    if not isinstance(usage, dict):
        return 0
    value = usage.get("input_tokens")
    return value if type(value) is int else 0


def scan_token_usage():
    total = 0
    maximum = 0
    raw_root = ROOT / "raw"
    if raw_root.exists():
        for path in sorted(raw_root.rglob("responses.jsonl")):
            for line in open(path, encoding="utf-8"):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                value = usage_input_tokens(record.get("response") if isinstance(record, dict) else None)
                total += value
                maximum = max(maximum, value)
    return total, maximum


def make_job(corpus, item, labels, tag, options=None):
    return {
        "corpus": corpus,
        "item": item,
        "labels": labels,
        "options": list(labels if options is None else options),
        "tag": tag,
    }


def build_step(corpus, step):
    items, labels = load_corpus(corpus)
    timeout = TIMEOUT_S
    if step == "smoke":
        selected = items[:3]
        phases = [[[make_job(corpus, item, labels, "smoke")] for item in selected]]
        outdir = ROOT / "raw" / "smoke" / corpus
        tags = ["smoke"]
    elif step in ("drift-start", "drift-end"):
        selected = items[:50]
        phases = [[[make_job(corpus, item, labels, step)] for item in selected]]
        outdir = ROOT / "raw" / "drift" / step.split("-")[-1] / corpus
        tags = [step]
    elif step in ("pass1", "pass2", "pass3"):
        phases = [[[make_job(corpus, item, labels, step)] for item in items]]
        outdir = ROOT / "raw" / step / corpus
        tags = [step]
        if corpus == "clinc150":
            timeout = CLINC_FULL_TIMEOUT_S
    elif step == "p2":
        if corpus != "banking77":
            raise SystemExit("the p2 step is Banking77 only")
        permutations = load_permutations(labels)
        pairs = []
        for item in items[:300]:
            pairs.append(
                [
                    make_job(corpus, item, labels, "O"),
                    make_job(corpus, item, labels, "S", permutations[item["id"]]),
                ]
            )
        again = [[make_job(corpus, item, labels, "O2")] for item in items[:50]]
        phases = [pairs, again]
        outdir = ROOT / "raw" / "order-probe" / corpus
        tags = ["O", "S", "O2"]
    else:
        raise SystemExit(f"unsupported step: {step}")
    planned = sum(len(group) for phase in phases for group in phase)
    return {
        "corpus": corpus,
        "step": step,
        "labels": labels,
        "phases": phases,
        "outdir": outdir,
        "tags": tags,
        "timeout_s": timeout,
        "planned_records": planned,
        "planned_items": len({job["item"]["id"] for phase in phases for group in phase for job in group}),
    }


def smoke_max_tokens(corpus):
    path = ROOT / "raw" / "smoke" / corpus / "responses.jsonl"
    if not path.exists():
        return None
    values = []
    for line in open(path, encoding="utf-8"):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        value = usage_input_tokens(record.get("response") if isinstance(record, dict) else None)
        if value:
            values.append(value)
    return max(values) if values else None


def check_projection():
    maxima = {corpus: smoke_max_tokens(corpus) for corpus in PLANNED_CALLS}
    if any(value is None for value in maxima.values()):
        raise SystemExit("smoke usage is missing; the step-4 cap projection cannot be computed")
    projected = sum(maxima[corpus] * PLANNED_CALLS[corpus] for corpus in PLANNED_CALLS)
    threshold = int(CAP_TOKENS * 0.8)
    result = {
        "max_smoke_input_tokens": maxima,
        "planned_calls": dict(PLANNED_CALLS),
        "projected_input_tokens": projected,
        "eighty_percent_of_cap": threshold,
    }
    if projected > threshold:
        raise SystemExit(
            f"cap projection {projected} exceeds 80% of the {CAP_TOKENS} token cap; step 4 must not start"
        )
    return result


def drift_start_anchor():
    candidates = []
    for corpus in ("banking77", "clinc150"):
        directory = ROOT / "raw" / "drift" / "start" / corpus
        manifest_path = directory / "MANIFEST.json"
        if manifest_path.exists():
            try:
                started = json.load(open(manifest_path, encoding="utf-8")).get("started")
                candidates.append(datetime.fromisoformat(started).timestamp())
            except Exception:
                pass
        responses = directory / "responses.jsonl"
        if responses.exists():
            for line in open(responses, encoding="utf-8"):
                try:
                    value = json.loads(line).get("ts")
                except Exception:
                    continue
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    candidates.append(float(value))
    return min(candidates) if candidates else None


def enforce_run_window(step):
    if step == "smoke":
        return
    anchor = drift_start_anchor()
    if anchor is None:
        if step != "drift-start":
            raise SystemExit("drift-start has not begun; steps 4-12 have no registered run-window anchor")
        return
    if time.time() - anchor > 24 * 60 * 60:
        raise SystemExit("the first drift-start call is more than 24 hours old; this step cannot start")


def build_manifest(args, step_def, freeze, meter, started, projection=None):
    corpus = step_def["corpus"] if step_def else None
    labels = step_def["labels"] if step_def else []
    label_path = ROOT / "labels" / f"{corpus}.json" if corpus else None
    capture = None
    capture_path = ROOT / "docs" / "CAPTURE.json"
    if capture_path.exists():
        try:
            loaded = json.load(open(capture_path, encoding="utf-8"))
            capture = {
                "captured_start_utc": loaded.get("captured_start_utc"),
                "captured_end_utc": loaded.get("captured_end_utc"),
            }
        except Exception:
            capture = None
    manifest = {
        "assay": "ASSAY-002",
        "step": args.step,
        "corpus": corpus,
        "tags": step_def["tags"] if step_def else [],
        "planned_records": step_def["planned_records"] if step_def else 1,
        "planned_items": step_def["planned_items"] if step_def else None,
        "n": step_def["planned_records"] if step_def else 1,
        "label_count": len(labels),
        "labels_file": f"labels/{corpus}.json" if corpus else None,
        "label_order_sha256": sha256_file(label_path) if label_path else None,
        "model_requested": MODEL,
        "api_url": MODELS_URL if args.step == "key-check" else API_URL,
        "instructions": INSTRUCTIONS.get(corpus),
        "workers_initial": 1 if args.step == "key-check" else args.workers,
        "workers_current": 1 if args.step == "key-check" else args.workers,
        "circuit_breaker_trips": [],
        "host": socket.gethostname(),
        "location": args.location,
        "started": started,
        "finished": None,
        "completed": False,
        "protocol_sha256": freeze["protocol_sha256"],
        "FREEZE.sha256": (ROOT / "FREEZE.sha256").read_text(encoding="utf-8"),
        "freeze_file_sha256": freeze["freeze_sha256"],
        "freeze_commit": git_head(),
        "CORPUS.sha256": (ROOT / "CORPUS.sha256").read_text(encoding="utf-8"),
        "DOCS.sha256": (ROOT / "DOCS.sha256").read_text(encoding="utf-8"),
        "docs_capture": capture,
        "timeout_s": step_def["timeout_s"] if step_def else TIMEOUT_S,
        "retry_policy": {
            "max_attempts": 8,
            "retry_statuses": "429 and 5xx",
            "backoff": "1 s doubling to 30 s; Retry-After wins when longer",
            "network_errors": "no retry",
        },
        "cap_tokens": CAP_TOKENS,
        "input_tokens_before_step": meter.total_tokens if meter else None,
        "max_input_tokens_seen_before_step": meter.max_seen if meter else None,
        "cap_projection": projection,
        "records_written": 0,
        "stop_reason": None,
    }
    if step_def and step_def["step"] == "p2":
        manifest["permutations_file"] = "labels/b77-permutations-300.json"
        manifest["permutations_sha256"] = sha256_file(ROOT / "labels/b77-permutations-300.json")
    return manifest


def summarize_responses(path: Path):
    records = []
    if path.exists():
        for line in open(path, encoding="utf-8"):
            if line.strip():
                records.append(json.loads(line))
    status_counts = Counter()
    attempt_counts = Counter()
    model_counts = Counter()
    token_sum = 0
    timestamps = []
    for record in records:
        response = record.get("response") if isinstance(record, dict) else None
        if not isinstance(response, dict):
            response = {}
        status = response.get("status")
        status_counts[str(status)] += 1
        attempt_counts[str(response.get("attempt"))] += 1
        token_sum += usage_input_tokens(response)
        if status == 200:
            body = response.get("body")
            model = body.get("model") if isinstance(body, dict) else None
            model_counts[model if isinstance(model, str) else json.dumps(model, sort_keys=True)] += 1
        ts = record.get("ts") if isinstance(record, dict) else None
        if isinstance(ts, (int, float)) and not isinstance(ts, bool):
            timestamps.append(float(ts))
    return {
        "records": records,
        "non_200_by_status": {
            key: status_counts[key] for key in sorted(status_counts) if key != "200"
        },
        "attempt_histogram": {key: attempt_counts[key] for key in sorted(attempt_counts)},
        "body_model_values": {key: model_counts[key] for key in sorted(model_counts)},
        "input_tokens_this_file": token_sum,
        "first_record_ts": min(timestamps) if timestamps else None,
        "last_record_ts": max(timestamps) if timestamps else None,
    }


class StepRunner:
    def __init__(self, key, step_def, workers, meter, log_handle):
        self.key = key
        self.step_def = step_def
        self.workers = workers
        self.meter = meter
        self.log_handle = log_handle
        self.control = RunControl()
        self.gate = ConcurrencyGate(workers, self.control)
        self.records_written = 0
        self.non_200 = 0
        self.failure = None
        self.circuit_breaker_trips = []
        self._last_100 = deque(maxlen=100)

    def _run_group(self, group):
        if self.control.stop_event.is_set():
            return []
        if not self.gate.acquire():
            return []
        records = []
        try:
            for job in group:
                if self.control.stop_event.is_set():
                    break
                estimate = self.meter.admit()
                if estimate is None:
                    self.control.request_stop("input-token cap reached before request admission")
                    break
                body = make_request(job["corpus"], job["item"], job["labels"], job["options"])
                try:
                    response = post(self.key, body, timeout=self.step_def["timeout_s"])
                finally:
                    pass
                self.meter.finish(estimate, usage_input_tokens(response))
                record = {
                    "id": job["item"]["id"],
                    "label": job["item"]["label"],
                    "tag": job["tag"],
                    "request": body,
                    "response": response,
                    "ts": time.time(),
                }
                records.append(record)
                if response.get("status") in (401, 402, 403):
                    self.control.request_stop(f"HTTP {response['status']} stop status received")
                    break
            return records
        finally:
            self.gate.release()

    def _write_record(self, record):
        self.log_handle.write(json.dumps(record) + "\n")
        self.log_handle.flush()
        self.records_written += 1
        response = record.get("response") or {}
        if response.get("status") != 200:
            self.non_200 += 1
        self._last_100.append(429 in (response.get("retries") or []))
        if len(self._last_100) == 100 and sum(self._last_100) >= 20:
            before, after = self.gate.trip()
            self.circuit_breaker_trips.append(
                {
                    "time": machine_now(),
                    "completed_requests": self.records_written,
                    "needed_429_retry_last_100": int(sum(self._last_100)),
                    "workers_before": before,
                    "workers_after": after,
                    "pause_s": 60,
                }
            )
            self._last_100.clear()
        if self.records_written % 100 == 0 or self.records_written == self.step_def["planned_records"]:
            print(
                f"{self.step_def['step']}/{self.step_def['corpus']}: "
                f"{self.records_written}/{self.step_def['planned_records']} non-200={self.non_200}",
                flush=True,
            )

    def execute(self):
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            for phase in self.step_def["phases"]:
                if self.control.stop_event.is_set():
                    break
                futures = [executor.submit(self._run_group, group) for group in phase]
                for future in as_completed(futures):
                    try:
                        records = future.result()
                    except Exception as exc:
                        self.failure = repr(exc)
                        self.control.request_stop(f"worker failure: {self.failure}")
                        continue
                    for record in records:
                        self._write_record(record)


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=1) + "\n", encoding="utf-8")


def refuse_existing_output(outdir: Path, filenames):
    existing = [name for name in filenames if (outdir / name).exists()]
    if existing:
        raise SystemExit(
            f"refusing to overwrite existing step output in {outdir}: {', '.join(existing)}"
        )


def execute_step(args, freeze) -> int:
    step_def = build_step(args.corpus, args.step)
    if args.dry_run:
        first_job = step_def["phases"][0][0][0]
        print(
            json.dumps(
                make_request(first_job["corpus"], first_job["item"], first_job["labels"], first_job["options"]),
                indent=1,
            )
        )
        return 0

    outdir = step_def["outdir"]
    refuse_existing_output(outdir, ["MANIFEST.json", "responses.jsonl", "responses.sha256"])
    projection = check_projection() if args.step == "drift-start" else None
    enforce_run_window(args.step)
    total_tokens, max_seen = scan_token_usage()
    meter = CapMeter(total_tokens, max_seen)
    if meter.stopped:
        raise SystemExit("the input-token cap has already been reached; no request will be sent")

    key = load_key()
    outdir.mkdir(parents=True, exist_ok=True)
    started = machine_now()
    manifest = build_manifest(args, step_def, freeze, meter, started, projection)
    write_json(outdir / "MANIFEST.json", manifest)

    responses_path = outdir / "responses.jsonl"
    runner = None
    log_handle = open(responses_path, "x", encoding="utf-8")
    try:
        runner = StepRunner(key, step_def, args.workers, meter, log_handle)
        try:
            runner.execute()
        except KeyboardInterrupt:
            runner.control.request_stop("interrupted by operator")
            runner.failure = "KeyboardInterrupt"
    finally:
        log_handle.close()
        digest = sha256_file(responses_path)
        (outdir / "responses.sha256").write_text(f"{digest}  responses.jsonl\n", encoding="utf-8")
        summary = summarize_responses(responses_path)
        manifest.update(
            {
                "finished": machine_now(),
                "completed": bool(
                    runner
                    and runner.records_written == step_def["planned_records"]
                    and runner.failure is None
                    and runner.control.stop_reason is None
                ),
                "records_written": runner.records_written if runner else 0,
                "non_200_by_status": summary["non_200_by_status"],
                "attempt_histogram": summary["attempt_histogram"],
                "body_model_values": summary["body_model_values"],
                "circuit_breaker_trips": runner.circuit_breaker_trips if runner else [],
                "workers_current": runner.gate.limit if runner else args.workers,
                "input_tokens_this_step": meter.step_tokens,
                "cumulative_input_tokens": meter.total_tokens,
                "max_input_tokens_seen": meter.max_seen,
                "first_record_ts": summary["first_record_ts"],
                "last_record_ts": summary["last_record_ts"],
                "responses_sha256": digest,
                "stop_reason": runner.control.stop_reason if runner else "runner did not start",
                "failure": runner.failure if runner else None,
            }
        )
        write_json(outdir / "MANIFEST.json", manifest)

    print(f"sealed {responses_path} sha256={digest}")
    if runner and (runner.failure or runner.control.stop_reason):
        print(f"step stopped: {runner.control.stop_reason or runner.failure}", file=sys.stderr)
        return 1
    return 0


def extract_model_ids(body):
    if isinstance(body, list):
        candidates = body
    elif isinstance(body, dict):
        candidates = body.get("data") or body.get("models") or []
    else:
        candidates = []
    ids = []
    for candidate in candidates if isinstance(candidates, list) else []:
        if isinstance(candidate, str):
            ids.append(candidate)
        elif isinstance(candidate, dict):
            value = candidate.get("id") or candidate.get("model") or candidate.get("name")
            if isinstance(value, str):
                ids.append(value)
    return ids


def execute_key_check(args, freeze) -> int:
    if args.dry_run:
        print(json.dumps({"method": "GET", "url": MODELS_URL, "model_required": MODEL}, indent=1))
        return 0
    outdir = ROOT / "raw" / "models"
    refuse_existing_output(outdir, ["MANIFEST.json", "response.json"])
    total_tokens, max_seen = scan_token_usage()
    meter = CapMeter(total_tokens, max_seen)
    key = load_key()
    outdir.mkdir(parents=True, exist_ok=True)
    started = machine_now()
    manifest = build_manifest(args, None, freeze, meter, started)
    write_json(outdir / "MANIFEST.json", manifest)

    request = urllib.request.Request(
        MODELS_URL,
        method="GET",
        headers={"Authorization": f"Bearer {key}", "User-Agent": USER_AGENT},
    )
    started_clock = time.perf_counter()
    status = 0
    body = None
    error = None
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            raw = response.read()
            status = int(response.status)
            try:
                body = json.loads(raw)
            except Exception:
                error = raw.decode(errors="replace")[:2000]
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        error = exc.read().decode(errors="replace")[:2000]
    except Exception as exc:
        error = repr(exc)[:2000]
    ms = round((time.perf_counter() - started_clock) * 1000, 1)
    model_ids = extract_model_ids(body)
    response_record = {
        "status": status,
        "ms": ms,
        "model_ids": model_ids,
        "body": body,
        "error": error,
        "ts": time.time(),
    }
    write_json(outdir / "response.json", response_record)
    completed = status == 200 and MODEL in model_ids
    manifest.update(
        {
            "finished": machine_now(),
            "completed": completed,
            "records_written": 1,
            "model_ids": model_ids,
            "stop_reason": None if completed else f"key check failed with status {status} or model absent",
            "cumulative_input_tokens": meter.total_tokens,
        }
    )
    write_json(outdir / "MANIFEST.json", manifest)
    print(f"key check status={status} models={model_ids}")
    return 0 if completed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="ASSAY-002 frozen runner")
    parser.add_argument("corpus", nargs="?", choices=["banking77", "clinc150"])
    parser.add_argument(
        "--step",
        required=True,
        choices=["key-check", "smoke", "drift-start", "pass1", "p2", "pass2", "pass3", "drift-end"],
    )
    parser.add_argument("--location", required=True, help="host location for MANIFEST.json; no default")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true", help="print the first request; loads no key and sends nothing")
    args = parser.parse_args()
    if not args.location.strip():
        parser.error("--location must not be empty")
    args.location = args.location.strip()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    if args.step == "key-check":
        if args.corpus is not None:
            parser.error("key-check does not take a corpus")
    elif args.corpus is None:
        parser.error("a corpus is required for every step except key-check")

    freeze = load_freeze()
    if args.step == "key-check":
        return execute_key_check(args, freeze)
    return execute_step(args, freeze)


if __name__ == "__main__":
    raise SystemExit(main())
