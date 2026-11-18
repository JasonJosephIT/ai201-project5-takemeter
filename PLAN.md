# Project 5 plan: TakeMeter, shape A (deploy and instrument), Path A (hosted)

## What's new
TakeMeter (Project 3) only ran in a notebook. The extension puts it behind a public URL on a Hugging Face Space (Gradio), with a structured log line for every request.

Out of scope: new labels, hardening (retries, rate limits, bad input), auth, UI polish.

Extra credit (declare in README before starting): latency breakdown per stage (tokenize, model, post-process, log write), measured with `time.perf_counter()` on every request.

## Five acceptance criteria (draft; finalise in criteria.md before any run)
1. Reachable (extension): the URL returns a label and confidence for a 50-word post within 5 s on a warm Space. 3/3 trials.
2. Logged (extension): every request writes one JSONL line with `ts`, `input`, `label`, `confidence`, `latency_ms`. 10/10 requests logged per trial, 0 missing fields.
3. Warm latency (extension): median `latency_ms` ≤ 500 ms over 20 requests.
4. Cold start (extension): the first request after the Space sleeps answers within 60 s.
5. Quality holds (system): macro-F1 ≥ 0.60 on the held-out test set, and hosted predictions match local predictions on 20 test posts (≥ 19/20).

## Logging
- Fields: `ts`, `input`, `label`, `confidence`, `latency_ms`, plus `t_tokenize_ms`, `t_model_ms`, `t_post_ms` (extra credit).
- Free Spaces wipe their disk on restart. Use `huggingface_hub.CommitScheduler` to push `logs/requests.jsonl` to a dataset repo every few minutes, and commit a downloaded copy to this repo.

## Cost
Seconds of CPU per request, measured from `latency_ms` in the logs (median and p90). Hosting on the free CPU tier costs $0, so state both numbers.

## Improvement (pick after the first results)
Likely: load the model once at startup and cap `max_length` at 256. Re-run all trials and show before and after side by side.

## Steps
| # | Step | Time |
|---|------|------|
| 0 | Train: run takemeter.ipynb sections 1–5, save the model | ~1 h |
| 1 | Write criteria.md (before deploying) | 20 min |
| 2 | Write app.py + requirements.txt with logging and stage timings | 45 min |
| 3 | Push the model to the Hub, create the Space, deploy | 30 min |
| 4 | Write RUNNING.md (URL, platform, deploy steps) | 10 min |
| 5 | Run 3 trials per criterion and fill in run_log.md | 45 min |
| 6 | Write the verdict and diagnosis for each criterion | 20 min |
| 7 | Make one improvement, re-run, put the two result sets side by side | 1 h |
| 8 | Finish README: extension, shape, out of scope, ≥10 log lines, cost, what's left | 30 min |

Total: about 5–6 hours.
