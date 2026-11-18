# Run log — before

Space `JasonJosephIT/takemeter`, `cpu-basic`, `max_length` 512, model seed 42 / 10 epochs. 2026-11-18. Raw data: `run_log.json`.

| # | Criterion | Target | Trial 1 | Trial 2 | Trial 3 | Verdict |
|---|---|---|---|---|---|---|
| 1 | Reachable | ≤ 5 s round trip | 436 ms | 345 ms | 430 ms | Pass |
| 2 | Logged | 10/10 complete | 10/10 | 10/10 | 10/10 | Pass |
| 3 | Warm latency | median ≤ 300 ms | 54.4 ms (max 281.5) | 46.5 ms (max 190.0) | 47.3 ms (max 187.1) | Pass |
| 4 | Cold start | ≤ 60 s | 16.0 s | 15.8 s | 16.2 s | Pass |
| 5a | Hosted = local | ≥ 19/20 | 20/20 | 20/20 | 20/20 | Pass |
| 5b | Macro-F1 | ≥ 0.60 | 0.357 | 0.357 | 0.357 | Miss |
| 6 | Ad precision | ≥ 0.70 | 0.714 | 0.714 | 0.714 | Pass |
| 7 | Truncation | 20/20 match | 20/20 | 20/20 | 20/20 | Pass |

Round-trip median from the client: 440 ms, 412 ms, 420 ms. Cold start is timed from `restart_space` after a confirmed pause, so it includes container start, model download and load.

## Sample log lines

```
{"ts": "2026-11-18T23:37:57.489672+00:00", "input": "warm-up request, not counted", "label": "explainer", "confidence": 0.2156, "n_tokens": 9, "truncated": false, "latency_ms": 21.8, "t_tokenize_ms": 0.5, "t_model_ms": 21.1, "t_post_ms": 0.2}
{"ts": "2026-11-18T23:37:57.936248+00:00", "input": "Our family bakery on Edgewater Drive is opening a second location in Winter Park this Saturday. The first fifty customers get a free dozen cookies, and we will have live music, face painting for kids and coffee from a local roaster all day. Come say hi, bring your neighbours and try our new guava cheese pastries.", "label": "advertisement", "confidence": 0.2573, "n_tokens": 68, "truncated": false, "latency_ms": 37.9, "t_tokenize_ms": 0.7, "t_model_ms": 37.1, "t_post_ms": 0.1}
{"ts": "2026-11-18T23:37:58.402414+00:00", "input": "Leiah closed unexpectedly tonight. Anyone know why?\n\nHad reservations at Leiah tonight at 6:30. Upon arrival the front doors were locked and we then realized there were no customers inside. We waited outside confused for a couple minutes and a police officer showed up and was let in to talk with a chef. We walked away with no answers and aside from being disappointed in beyond curious. Anyone knows what's up?", "label": "reaction", "confidence": 0.2762, "n_tokens": 86, "truncated": false, "latency_ms": 69.0, "t_tokenize_ms": 1.0, "t_model_ms": 68.0, "t_post_ms": 0.1}
```
