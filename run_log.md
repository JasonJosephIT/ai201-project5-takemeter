# Run log: before (128 tokens) vs after (512 tokens)

Same Space (`JasonJosephIT/takemeter`, `cpu-basic`), same seed-42 split and test posts, same `trials.py`.
Only change: `max_length` 128 → 512, model retrained (seed 42, 10 epochs). Before = Hub revision `40417fc`.
Each cell lists trials 1 / 2 / 3. Raw data: `run_log_128.json`, `run_log_512.json`.

| # | Criterion | Before: 128 tokens | Verdict | After: 512 tokens | Verdict |
|---|---|---|---|---|---|
| 1 | Reachable ≤ 5 s | 402 ms / 385 ms / 404 ms | Pass | 436 ms / 345 ms / 430 ms | Pass |
| 2 | Logged 10/10 | 10/10 / 10/10 / 10/10 | Pass | 10/10 / 10/10 / 10/10 | Pass |
| 3 | Median latency ≤ 300 ms | 54.4 ms / 53.0 ms / 57.3 ms | Pass | 54.4 ms / 46.5 ms / 47.3 ms | Pass |
| 4 | Cold start ≤ 60 s | 14.6 s / 14.3 s / 14.8 s | Pass | 16.0 s / 15.8 s / 16.2 s | Pass |
| 5a | Hosted = local ≥ 19/20 | 20/20 / 20/20 / 20/20 | Pass | 20/20 / 20/20 / 20/20 | Pass |
| 5b | Macro-F1 ≥ 0.60 | 0.278 / 0.278 / 0.278 | Miss | 0.357 / 0.357 / 0.357 | Miss |
| 6 | Ad precision ≥ 0.70 | 0.8 / 0.8 / 0.8 | Pass | 0.714 / 0.714 / 0.714 | Pass |
| 7 | Truncation 20/20 | 20/20 / 20/20 / 20/20 | Pass | 20/20 / 20/20 / 20/20 | Pass |

Slowest warm request: before 106.1 ms, 99.6 ms, 85.4 ms; after 281.5 ms, 190.0 ms, 187.1 ms.
Posts in `labels.csv` longer than the limit: 34% at 128, 5% (10/215) at 512.
Cold start = pause the Space, confirm it stopped answering, restart, time to the first answer.
5b and 6 score the same 33 test posts each trial, so they do not vary between trials.

## Sample log lines (after, 512)

```
{"ts": "2026-11-18T23:37:57.489672+00:00", "input": "warm-up request, not counted", "label": "explainer", "confidence": 0.2156, "n_tokens": 9, "truncated": false, "latency_ms": 21.8, "t_tokenize_ms": 0.5, "t_model_ms": 21.1, "t_post_ms": 0.2}
{"ts": "2026-11-18T23:37:57.936248+00:00", "input": "Our family bakery on Edgewater Drive is opening a second location in Winter Park this Saturday. The first fifty customers get a free dozen cookies, and we will have live music, face painting for kids and coffee from a local roaster all day. Come say hi, bring your neighbours and try our new guava cheese pastries.", "label": "advertisement", "confidence": 0.2573, "n_tokens": 68, "truncated": false, "latency_ms": 37.9, "t_tokenize_ms": 0.7, "t_model_ms": 37.1, "t_post_ms": 0.1}
{"ts": "2026-11-18T23:37:58.402414+00:00", "input": "Leiah closed unexpectedly tonight. Anyone know why?\n\nHad reservations at Leiah tonight at 6:30. Upon arrival the front doors were locked and we then realized there were no customers inside. We waited outside confused for a couple minutes and a police officer showed up and was let in to talk with a chef. We walked away with no answers and aside from being disappointed in beyond curious. Anyone knows what's up?", "label": "reaction", "confidence": 0.2762, "n_tokens": 86, "truncated": false, "latency_ms": 69.0, "t_tokenize_ms": 1.0, "t_model_ms": 68.0, "t_post_ms": 0.1}
```
