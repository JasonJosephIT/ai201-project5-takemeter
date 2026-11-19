# TakeMeter, hosted (Project 5)

TakeMeter labels a post from a local subreddit with one of six labels: `analysis`,
`hot_take`, `reaction`, `explainer`, `anecdote` or `advertisement`. In Project 3 it only
ran inside a notebook. This extension puts it behind a public URL and logs every request.

- **Live demo:** https://jasonjosephit.github.io/ai201-project5-takemeter/
- **Space (app + API):** https://huggingface.co/spaces/JasonJosephIT/takemeter
- **Model:** https://huggingface.co/JasonJosephIT/takemeter
- **Run and redeploy:** [RUNNING.md](RUNNING.md)

## Extension

| | |
|---|---|
| Shape | A: deploy and instrument |
| Path | A: hosted on a Hugging Face Space (Gradio, `cpu-basic`) |
| Extra credit (declared before starting) | Per-stage latency breakdown: tokenize, model, post-process, measured with `time.perf_counter()` on every request |
| Out of scope | New labels, hardening (retries, rate limits, bad input), auth, UI polish |

A browser demo page on GitHub Pages ([docs/index.html](docs/index.html)) calls the Space's
`/classify` API directly. The Space allows requests from the `github.io` address.

## How a request flows

```
browser (GitHub Pages)
   │  POST /gradio_api/call/classify
   ▼
Hugging Face Space ── tokenize (≤ 512 tokens) ── DistilBERT ── softmax → label ── write log line
   │
   ▼  label + six confidences
browser
```

Each request writes one JSON line to `requests.jsonl` and prints it to the Space's Logs tab.

| Field | Meaning |
|---|---|
| `ts`, `input`, `label`, `confidence` | When, what was sent, the answer, its probability |
| `latency_ms` | Total server time for the request |
| `t_tokenize_ms`, `t_model_ms`, `t_post_ms` | Time per stage (extra credit) |
| `n_tokens`, `truncated` | Full token count, and whether it went past the 512-token limit |

## Acceptance criteria

Full targets and reasons: [criteria.md](criteria.md), written before any run. Criteria 1–4, 5a and 7
test the deployment; 5b and 6 test the model's output.

## Results: before and after the improvement

The trials are in [trials.py](trials.py): each warm trial sends a 50-word post plus all 33
held-out test posts, and each cold trial pauses the Space, confirms it stopped answering,
restarts it and times the first answer. 3 warm and 3 cold trials per run. Values are
trials 1 / 2 / 3. Raw data: [run_log_128.json](run_log_128.json), [run_log_512.json](run_log_512.json);
table: [run_log.md](run_log.md).

| # | Criterion | Before: 128 tokens | | After: 512 tokens | |
|---|---|---|---|---|---|
| 1 | Answers within 5 s | 402 / 385 / 404 ms | Pass | 436 / 345 / 430 ms | Pass |
| 2 | 10/10 requests logged, all fields | 10/10 ×3 | Pass | 10/10 ×3 | Pass |
| 3 | Median server time ≤ 300 ms | 54.4 / 53.0 / 57.3 ms | Pass | 54.4 / 46.5 / 47.3 ms | Pass |
| 4 | Cold start ≤ 60 s | 14.6 / 14.3 / 14.8 s | Pass | 16.0 / 15.8 / 16.2 s | Pass |
| 5a | Hosted = local ≥ 19/20 | 20/20 ×3 | Pass | 20/20 ×3 | Pass |
| 5b | Macro-F1 ≥ 0.60 | 0.278 | **Miss** | 0.357 | **Miss** |
| 6 | Ad precision ≥ 0.70 | 0.800 | Pass | 0.714 | Pass |
| 7 | Truncation flag matches local 20/20 | 20/20 ×3 | Pass | 20/20 ×3 | Pass |

5b and 6 score the same 33 test posts every trial, so they do not move between trials; the
three trials only show the hosted answers are stable.

### Verdicts and diagnosis

- **1–4, 5a, 7 pass with room to spare.** The deployment does what it promised. Warm requests
  take about 50 ms on the server; most of the ~400 ms round trip is network and Gradio's
  two-step call. Cold start is about 15 s, well under 60 s.
- **5b misses (0.36 against 0.60).** This is a model problem, not a deployment problem: 5a shows
  the hosted model gives the same answers as the local one. Per-label F1 (512 tokens):
  `advertisement` 0.77, `analysis` 0.50, `reaction` 0.36, `explainer` 0.29, `anecdote` 0.22,
  `hot_take` 0.00. The model never gets a `hot_take` right: 3 of 6 are called `analysis`. It has
  learned "takes a position" but not "backed by a checkable fact". The next biggest mix-up is
  `reaction` vs `anecdote` (3 posts), where only timing separates the labels. These are the same
  two boundaries the Project 3 diagnosis found. With 24 `hot_take` posts in training, there
  is too little data to learn the difference.
- **6 passes, but by one post.** Precision fell from 0.80 to 0.71 after the change: 5 of 7 ad calls
  were right. One of the false ads is the edge case the definition already rules out (a customer
  praising a burger place).

## The improvement: read more of each post

**What changed:** `max_length` 128 → 512 (DistilBERT's maximum), then retrained. Same data, seed
(42), epochs (10) and test posts.

**Why:** the model only read the first 128 tokens, and 34% of the 215 posts are longer
(77% of `analysis`, 49% of `advertisement`). The Project 3 diagnosis said the deciding cue often
sits past the cut.

| | 128 tokens | 512 tokens |
|---|---|---|
| Posts cut short | 34% | 5% (10 of 215) |
| Macro-F1 | 0.28 | 0.36 |
| Accuracy | 0.30 | 0.39 |
| Median server time | 53–57 ms | 47–54 ms |
| Slowest warm request | 85–106 ms | 187–282 ms |
| `explainer` / `anecdote` F1 | 0.14 / 0.00 | 0.29 / 0.22 |

It helped, with no cost to the median: macro-F1 rose 0.08, and `anecdote` went from never right
to partly right. It did not reach the 0.60 target, and the slowest requests (long posts) are about
twice as slow. The 1,120-token post took 237 ms on the server.

## Sample log lines

12 requests from 2026-11-19, from the Space's Logs tab. `input` is shortened to 60 characters here;
the log stores the full post. All fields are in [sample_logs.json](sample_logs.json).

```json
{"ts":"2026-11-19T00:52:03.657175+00:00","input":"Leiah closed unexpectedly tonight. Anyone know why?  Had res…","label":"reaction","confidence":0.2762,"latency_ms":53.9,"t_tokenize_ms":0.9,"t_model_ms":52.9,"t_post_ms":0.1,"n_tokens":86,"truncated":false}
{"ts":"2026-11-19T00:52:04.014773+00:00","input":"Holy shit that was the brightest rocket launch I have seen f…","label":"reaction","confidence":0.2566,"latency_ms":25.0,"t_tokenize_ms":0.5,"t_model_ms":24.4,"t_post_ms":0.1,"n_tokens":24,"truncated":false}
{"ts":"2026-11-19T00:52:04.502975+00:00","input":"Turo (RICARDO FIGUEIREDO) BEWARE  At 5:22pm TODAY I gained a…","label":"analysis","confidence":0.3321,"latency_ms":185.5,"t_tokenize_ms":2.5,"t_model_ms":182.9,"t_post_ms":0.1,"n_tokens":416,"truncated":false}
{"ts":"2026-11-19T00:52:04.820833+00:00","input":"Petition: “To The X who did Y” Type posts should be banned. …","label":"explainer","confidence":0.2456,"latency_ms":46.0,"t_tokenize_ms":0.8,"t_model_ms":45.2,"t_post_ms":0.1,"n_tokens":78,"truncated":false}
{"ts":"2026-11-19T00:52:05.257949+00:00","input":"Scammers at Winter Park Village  Heads up: there are some te…","label":"reaction","confidence":0.2504,"latency_ms":45.1,"t_tokenize_ms":0.9,"t_model_ms":44.0,"t_post_ms":0.3,"n_tokens":77,"truncated":false}
{"ts":"2026-11-19T00:52:05.728038+00:00","input":"Since everyone was postiny about it being \"unfair\"  On the p…","label":"analysis","confidence":0.3149,"latency_ms":52.0,"t_tokenize_ms":1.0,"t_model_ms":51.0,"t_post_ms":0.1,"n_tokens":100,"truncated":false}
{"ts":"2026-11-19T00:52:06.125037+00:00","input":"With the recent ebike hysteria in Orlando, I feel like this …","label":"explainer","confidence":0.2587,"latency_ms":39.6,"t_tokenize_ms":0.9,"t_model_ms":38.7,"t_post_ms":0.1,"n_tokens":60,"truncated":false}
{"ts":"2026-11-19T00:52:06.692720+00:00","input":"Central Florida Metalcore Band Seeking Bassist w/ Harsh Voca…","label":"advertisement","confidence":0.2814,"latency_ms":75.0,"t_tokenize_ms":1.4,"t_model_ms":73.5,"t_post_ms":0.1,"n_tokens":161,"truncated":false}
{"ts":"2026-11-19T00:52:06.988053+00:00","input":"Uh…what the heck is this?  Just saw it 5 min ago…","label":"reaction","confidence":0.2665,"latency_ms":22.0,"t_tokenize_ms":0.4,"t_model_ms":21.5,"t_post_ms":0.1,"n_tokens":16,"truncated":false}
{"ts":"2026-11-19T00:52:07.401906+00:00","input":"Gringos Locos Closure Got Messy…","label":"reaction","confidence":0.2546,"latency_ms":24.2,"t_tokenize_ms":0.7,"t_model_ms":23.4,"t_post_ms":0.1,"n_tokens":9,"truncated":false}
{"ts":"2026-11-19T00:52:07.869266+00:00","input":"Orlando had one of the lowest murder rates in 2025 of all ma…","label":"analysis","confidence":0.3739,"latency_ms":99.9,"t_tokenize_ms":1.4,"t_model_ms":98.3,"t_post_ms":0.2,"n_tokens":216,"truncated":false}
{"ts":"2026-11-19T00:52:08.234798+00:00","input":"Homeschool trip ideas in Central Florida?  Trying to plan so…","label":"explainer","confidence":0.2354,"latency_ms":51.1,"t_tokenize_ms":1.0,"t_model_ms":50.1,"t_post_ms":0.1,"n_tokens":93,"truncated":false}
```

**Latency breakdown (extra credit), median of these 12:** total 48.6 ms = tokenize 0.9 ms +
model 47.7 ms + post-process 0.1 ms. The model is 98% of the server time, so a faster tokenizer
or post-processing step would not help; only a smaller model or faster hardware would. Model time
grows with post length: 9 tokens took 23 ms, 416 tokens took 183 ms.

## Cost

| Item | Cost |
|---|---|
| Hugging Face PRO (required to run a Gradio Space on `cpu-basic`) | $9 / month |
| `cpu-basic` hardware | $0 |
| Model repo on the Hub | $0 |
| GitHub Pages | $0 |
| Training (local, Apple Silicon GPU) | $0, about 1 minute per run |

Hugging Face now requires PRO to host Gradio or Docker Spaces on free CPU; only static Spaces are
free. Nebius was considered and not used: its hosted inference is built for large chat models,
and custom weights there are in beta and need a support request.

## What's still broken

- **`hot_take` scores 0.** The model reads opinions as `analysis` (see diagnosis above).
- **Logs do not survive a restart.** Free Space disk is wiped on restart; the Logs tab and
  `requests.jsonl` both reset. Copy lines out before restarting.
- **A bare link is read as text.** Pasting a URL instead of the post's text gets `advertisement`
  (0.29), because the app never opens the link.
- **Low confidence everywhere.** The top label is usually 0.23–0.37, so confidence cannot yet flag
  which answers to trust.
- **Small test set.** 5–6 posts per label, so one post moves a label's F1 by about 0.15–0.2. All
  numbers here are seed 42 only.
- **The 48-hour sleep was not tested.** Cold start was measured by pause and restart, which stands
  in for a Space waking after 48 hours with no traffic.

## Future improvements

- **Merge `reaction` and `anecdote`** into one "lived it" label. An estimate from the current
  predictions, without retraining, puts it at 17 of 33 right instead of 13. Report the six-label
  and merged scores side by side, and keep the 0.60 target.
- **Paste a link and extract the post.** If the input is a URL, the Space calls Tavily Extract or
  Firecrawl to fetch the title and body, then classifies it. The API key would be a Space secret,
  never in the page. This ties TakeMeter to the tool-calling projects. It needs its own criteria
  (extraction success rate, added latency) and a daily cap, since the demo is public.
- **Keep logs past restarts** with `huggingface_hub.CommitScheduler`, pushing `requests.jsonl` to a
  dataset repo every few minutes.

## Files

| File | What it is |
|---|---|
| [space/app.py](space/app.py) | The Gradio app: classify, time each stage, write the log line |
| [train_save.py](train_save.py) | Trains with the notebook's settings and saves `./model` (`EPOCHS=10 python train_save.py`) |
| [trials.py](trials.py) | Runs all criteria against the live Space |
| [criteria.md](criteria.md) | The 7 criteria, written before any run |
| [run_log.md](run_log.md) | Before/after results table |
| [docs/index.html](docs/index.html) | The GitHub Pages demo |
| `labels.csv`, `takemeter.ipynb` | Data and notebook from Project 3 (original labels, before the Project 3 relabel) |
