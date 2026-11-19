"""Run the criteria.md trials against the live Space and write run_log.json.

Each warm trial sends a 50-word post (criterion 1) and all 33 test posts. From those:
  2 logged      first 10 test posts have a log line with every field
  3 latency     median server latency_ms over the first 20 test posts
  5a parity     hosted label == local ./model label on the first 20 test posts
  7 truncation  logged n_tokens / truncated == local tokenizer on the first 20
  5b, 6         macro-F1 and advertisement precision over all 33 hosted labels
Cold-start trials (criterion 4) pause the Space, restart it and time the first answer.

Run: python trials.py [--trials 3] [--cold 3]
"""
import argparse
import json
import statistics
import time

import pandas as pd
import requests
from huggingface_hub import HfApi, get_token
from sklearn.metrics import f1_score, precision_score
from transformers import AutoTokenizer, pipeline

SPACE = "JasonJosephIT/takemeter"
URL = "https://jasonjosephit-takemeter.hf.space/gradio_api/call/classify"
LOGS = f"https://huggingface.co/api/spaces/{SPACE}/logs/run"
MAX_LENGTH = 512
FIELDS = ["ts", "input", "label", "confidence", "latency_ms", "t_tokenize_ms",
          "t_model_ms", "t_post_ms", "n_tokens", "truncated"]
POST_50 = ("Our family bakery on Edgewater Drive is opening a second location in Winter Park "
           "this Saturday. The first fifty customers get a free dozen cookies, and we will have "
           "live music, face painting for kids and coffee from a local roaster all day. Come say "
           "hi, bring your neighbours and try our new guava cheese pastries.")


def classify(text, timeout=120):
    """Call /classify; return (label, round_trip_ms)."""
    start = time.perf_counter()
    eid = requests.post(URL, json={"data": [text]}, timeout=timeout).json()["event_id"]
    body = requests.get(f"{URL}/{eid}", timeout=timeout).text
    ms = (time.perf_counter() - start) * 1000
    data = body.split("event: complete", 1)[1].split("data:", 1)[1].strip().splitlines()[0]
    return json.loads(data)[0]["label"], ms


def read_logs():
    """All JSON request lines currently in the Space's run log."""
    rows = []
    r = requests.get(LOGS, headers={"Authorization": f"Bearer {get_token()}"},
                     stream=True, timeout=10)
    try:
        for line in r.iter_lines(decode_unicode=True):
            if line and line.startswith("data:") and "n_tokens" in line:
                try:
                    rows.append(json.loads(json.loads(line[5:])["data"]))
                except (json.JSONDecodeError, KeyError):
                    pass
    except requests.exceptions.RequestException:
        pass  # the stream stays open; a read timeout just ends it
    return rows


def warm_trial(n, test, local_labels, tok):
    t_start = pd.Timestamp.now(tz="UTC").isoformat()
    classify("warm-up request, not counted")
    label_50, ms_50 = classify(POST_50)
    hosted = [classify(t) for t in test.text]
    time.sleep(5)
    logs = [r for r in read_logs() if r["ts"] >= t_start]
    by_input = {}
    for r in logs:
        by_input.setdefault(r["input"], r)

    texts = list(test.text)
    first10, first20 = texts[:10], texts[:20]
    logged = [by_input.get(t) for t in first10]
    complete = [r for r in logged if r and all(f in r for f in FIELDS)]
    lat = [by_input[t]["latency_ms"] for t in first20 if t in by_input]
    hosted_labels = [h[0] for h in hosted]
    parity = sum(h == l for h, l in zip(hosted_labels[:20], local_labels[:20]))
    trunc_ok = 0
    for t in first20:
        r, n_tok = by_input.get(t), len(tok(t)["input_ids"])
        if r and r["n_tokens"] == n_tok and r["truncated"] == (n_tok > MAX_LENGTH):
            trunc_ok += 1
    gold = list(test.label)
    return {
        "trial": n, "started": t_start,
        "c1_round_trip_ms": round(ms_50), "c1_label": label_50,
        "c2_logged_complete": f"{len(complete)}/10",
        "c3_median_latency_ms": round(statistics.median(lat), 1) if lat else None,
        "c3_n": len(lat), "c3_max_latency_ms": max(lat) if lat else None,
        "round_trip_median_ms": round(statistics.median(h[1] for h in hosted)),
        "c5a_parity": f"{parity}/20",
        "c5b_macro_f1": round(f1_score(gold, hosted_labels, average="macro", zero_division=0), 3),
        "c6_ad_precision": round(precision_score(gold, hosted_labels, labels=["advertisement"],
                                                 average="macro", zero_division=0), 3),
        "c7_truncation_match": f"{trunc_ok}/20",
        "sample_log_lines": logs[:3],
    }


def cold_trial(n, api):
    """Pause the Space (container stopped), then restart and time the first answer."""
    api.pause_space(SPACE)
    t = time.perf_counter()
    while api.get_space_runtime(SPACE).stage != "PAUSED":
        if time.perf_counter() - t > 120:
            return {"trial": n, "c4_cold_start_s": None, "error": "never reached PAUSED"}
        time.sleep(2)
    try:
        classify(POST_50, timeout=10)
        return {"trial": n, "c4_cold_start_s": None, "error": "answered while PAUSED"}
    except Exception:
        pass  # expected: nothing is serving
    api.restart_space(SPACE)
    start = time.perf_counter()
    while True:
        try:
            label, _ = classify(POST_50, timeout=30)
            return {"trial": n, "c4_cold_start_s": round(time.perf_counter() - start, 1),
                    "label": label}
        except Exception:
            if time.perf_counter() - start > 600:
                return {"trial": n, "c4_cold_start_s": None, "error": "no answer in 600 s"}
            time.sleep(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--cold", type=int, default=3)
    ap.add_argument("--model-dir", default="model", help="local model to compare against (5a)")
    ap.add_argument("--max-length", type=int, default=512, help="token limit the Space uses")
    ap.add_argument("--out", default="run_log.json")
    args = ap.parse_args()
    global MAX_LENGTH
    MAX_LENGTH = args.max_length

    test = pd.read_csv("test_split.csv")
    test["text"] = test["text"].astype(str)
    tok = AutoTokenizer.from_pretrained(args.model_dir)
    clf = pipeline("text-classification", model=args.model_dir, truncation=True, max_length=MAX_LENGTH)
    local_labels = [r["label"] for r in clf(list(test.text))]

    out = {"space": SPACE, "max_length": MAX_LENGTH, "hardware": "cpu-basic",
           "warm": [], "cold": []}
    for i in range(1, args.trials + 1):
        r = warm_trial(i, test, local_labels, tok)
        out["warm"].append(r)
        print(json.dumps({k: v for k, v in r.items() if k != "sample_log_lines"}), flush=True)
    api = HfApi()
    for i in range(1, args.cold + 1):
        r = cold_trial(i, api)
        out["cold"].append(r)
        print(json.dumps(r), flush=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
