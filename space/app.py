"""TakeMeter on a Hugging Face Space: classify a post, log one JSON line per request."""
import datetime
import json
import time

import gradio as gr
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL = "JasonJosephIT/takemeter"
MAX_LENGTH = 512
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL).eval()


def classify(text):
    t0 = time.perf_counter()
    n_tokens = len(tok(text)["input_ids"])  # full length, before the cut
    enc = tok(text, truncation=True, max_length=MAX_LENGTH, return_tensors="pt")
    t1 = time.perf_counter()
    with torch.no_grad():
        probs = model(**enc).logits.softmax(-1)[0]
    t2 = time.perf_counter()
    i = int(probs.argmax())
    label, conf = model.config.id2label[i], float(probs[i])
    scores = {model.config.id2label[j]: float(p) for j, p in enumerate(probs)}
    t3 = time.perf_counter()
    rec = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "input": text, "label": label, "confidence": round(conf, 4),
        "n_tokens": n_tokens, "truncated": n_tokens > MAX_LENGTH,
        "latency_ms": round((t3 - t0) * 1000, 1),
        "t_tokenize_ms": round((t1 - t0) * 1000, 1),
        "t_model_ms": round((t2 - t1) * 1000, 1),
        "t_post_ms": round((t3 - t2) * 1000, 1),
    }
    with open("requests.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)  # also lands in the Space's Logs tab
    return scores


gr.Interface(
    classify,
    gr.Textbox(lines=5, label="Post"),
    gr.Label(num_top_classes=6, label="TakeMeter"),
    title="TakeMeter",
    description="Labels a local-subreddit post: analysis, hot_take, reaction, explainer, anecdote or advertisement.",
).launch()
