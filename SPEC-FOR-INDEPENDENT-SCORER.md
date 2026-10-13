Write two self-contained Python 3 scripts, rescore.py and pairs.py, using only the
standard library and numpy. Print JSON only. Do not explain.

DEFINITIONS
- A "number" is a JSON int or float that is not a boolean, not NaN and not infinite.
- Record shape, one JSON object per line (any field may be missing or malformed;
  the rules say what to do; "tag" may be absent):
  {"id": str, "label": str, "tag": str,
   "response": {"status": int, "ms": float|null, "attempt": int,
                "body": {"model": str,
                         "answers": {"intent": {"type": str, "choice": str,
                                                "probabilities": {option: number},
                                                "confidence": number}},
                         "usage": {"input_tokens": int, "output_tokens": int}}}}
- ECE10(values, outcomes): 10 equal-width bins. Bin 0 covers [0, 0.1]; bin i
  (i = 1..9) covers (i/10, (i+1)/10]. For each bin with n > 0: mean_v = mean(values),
  acc = mean(outcomes), gap = mean_v - acc. ECE10 = sum over populated bins of
  (n / N) * |gap|.
- Wilson(k, n): 95% Wilson score interval, z = 1.959964.

rescore.py
INPUT: argv[1] = responses.jsonl. argv[2] = JSON file holding the list of K label
strings. argv[3] (optional) = the out-of-scope label (e.g. "oos").

R1. records = number of lines. non_200 = records with status != 200; also
    non_200_by_status = {status: count}.
R2. For each status-200 record, note which checks fail:
    a answers.intent is an object
    b answers.intent.type == "choice"
    c choice is a string in the label set
    d probabilities is an object
    e set of probabilities keys == label set
    f every probabilities value is a number in [0, 1]
    g d and f hold and abs(sum(values) - 1) <= 0.02 (if d or f fails, g fails)
    h confidence is a number in [0, 1]
    violations = records failing any of a-h.
    violations_documented = records failing any of a-f.
    violations_undocumented_only = records passing a-f and failing g or h.
    Over records where d and f hold: sum_min, sum_max, and
    sum_off_1e3 = count with abs(sum - 1) > 0.001.
R3. Calibration set = status-200 records where a holds, c holds, d holds, choice is a
    key of probabilities, and probabilities[choice] is a number in [0, 1].
    scored = N = its size. Failing b, e, g or h does NOT remove a record.
    Sort the calibration set by id (ascending string order); use that order below.
R4. For each calibration record: p = probabilities[choice];
    correct = 1 if choice == label else 0.
R5. ECE = ECE10(p, correct). bins = list of {bin, n, mean_p, acc, gap} for populated
    bins. MCE_all = max |gap| over populated bins. MCE_50 = max |gap| over bins with
    n >= 50 (null if none).
R6. ECE_equal_mass: sort the calibration set by (p, id); split into 10 parts with
    numpy.array_split; sum over parts of (n_part / N) * |mean_p - acc|.
R7. Brier = mean over calibration records of the sum over the K labels of
    (q_k - y_k)^2, where q_k = probabilities[k] if it is a number, else 0, and
    y_k = 1 if k == label else 0.
R8. accuracy = mean(correct). mean_p = mean(p). signed_gap = mean_p - accuracy.
R9. direction, over bins with n >= 50: "over" if every one has gap >= 0; "under" if
    every one has gap <= 0; "mixed" otherwise; "undetermined" if there are none.
R10. Bootstrap: rng = numpy.random.default_rng(2002). Repeat 2000 times:
     idx = rng.integers(0, N, size=N); compute ECE10(p[idx], correct[idx]).
     ECE_ci = [2.5th, 97.5th percentile] (numpy.percentile, default linear).
R11. Noise floor: rng = numpy.random.default_rng(2003). Repeat 2000 times:
     y = (rng.random(N) < p).astype(int); compute ECE10(p, y).
     noise_mean = mean; noise_p95 = 95th percentile.
R12. For S in {"gt09": p > 0.9, "ge09": p >= 0.9, "atom1": round(p, 6) == 1.0}:
     n, share = n / N, acc = mean(correct over S) (null if empty),
     wilson = Wilson(sum(correct over S), n).
     floor (S = gt09): wrong_all = N - sum(correct);
     wrong_shipped = n_gt09 - sum(correct over gt09); right_share_shipped = acc of
     gt09; refused_share = 1 - n_gt09 / N.
R13. argmax_exceptions = calibration records where d and f hold and
     p < max(values) - 1e-9.
R14. Latency over status-200 records with attempt == 1 and ms a number:
     latency_median, latency_p95, latency_p99 (numpy.percentile, default linear).
R15. attempts = {attempt: count} over all records. models = {body.model: count} over
     status-200 records. input_tokens_sum = sum of usage.input_tokens over status-200
     records where it is an int.
R16. Confidence (secondary): calibration records where confidence is a number in
     [0, 1]. Sort by (confidence, id); split into 10 parts with numpy.array_split;
     per part: n, mean_confidence, accuracy. conf_monotone = true if accuracy never
     decreases from part 1 to part 10. ECE_conf = ECE10(confidence, correct).
     conf_atom1_share = share with round(confidence, 6) == 1.0.
R17. Out-of-scope, only if argv[3] is given. Over the calibration set:
     oos = (label == argv[3]); inscope = not oos. Report n_oos, n_inscope, acc_oos,
     acc_inscope, mean_p_oos, mean_p_inscope, mean_conf_oos and mean_conf_inscope
     (over records with numeric confidence), and high_p_wrong_oos = (count of oos
     records with correct == 0 and p > 0.9) / n_oos.
     AUROC = (R - n_inscope * (n_inscope + 1) / 2) / (n_inscope * n_oos), where R is
     the sum of the ranks of the in-scope p values among all calibration p values
     (ranks start at 1; tied values get the average of their ranks).

OUTPUT: one JSON object, keys in this order, floats rounded to 4 dp, latency to 1 dp:
records, non_200, non_200_by_status, scored, violations, violations_documented,
violations_undocumented_only, sum_min, sum_max, sum_off_1e3, accuracy, mean_p,
signed_gap, ECE, ECE_ci, noise_mean, noise_p95, ECE_equal_mass, MCE_all, MCE_50,
Brier, direction, bins, gt09, ge09, atom1, floor, argmax_exceptions, latency_median,
latency_p95, latency_p99, attempts, models, input_tokens_sum, conf_deciles,
conf_monotone, ECE_conf, conf_atom1_share, oos (object, or null)

pairs.py
INPUT: argv[1] = file A, argv[2] = file B (both responses.jsonl). Optional
argv[3] = tag to keep from A, argv[4] = tag to keep from B ("-" keeps all).

Q1. Build the R3 calibration set of each file after the tag filter. Join on id; keep
    ids present in both. n_pairs = number joined.
Q2. flips = count where choice_A != choice_B. flip_rate = flips / n_pairs.
Q3. Over flips: both_le09 = count with p_A <= 0.9 and p_B <= 0.9;
    both_lt09 = count with p_A < 0.9 and p_B < 0.9; acc_A_flipped; acc_B_flipped.
Q4. Over stable pairs (same choice): acc_stable; absdp = |p_A - p_B|;
    absdp_median; absdp_gt005_share = share with absdp > 0.05.
Q5. cross_09 = count of joined pairs where exactly one of p_A > 0.9, p_B > 0.9 holds.

OUTPUT keys in this order: n_pairs, flips, flip_rate, both_le09, both_lt09,
acc_A_flipped, acc_B_flipped, acc_stable, absdp_median, absdp_gt005_share, cross_09
