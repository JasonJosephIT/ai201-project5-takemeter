---
status: active
progress: before-trials done, 7/8 pass; next is diagnosis + improvement
next_date:
updated: 2026-11-18
---

## Now
- 2026-11-18: Before-trials done (run_log.md / run_log.json, trials.py): 7 of 8 pass. 5b macro-F1 0.357 misses 0.60. 6 ad precision 0.714 passes by one post. Cold start 16 s (pause -> restart). Next: verdicts + diagnosis, then pick an improvement (token limit already used).
labels.csv final: 215 rows (40 explainer, 35 each of the other five), reviewed and confirmed by me. Copied to the Project 3 repo.

## Next
- Improvement (after hosting is confirmed): consolidate labels. Estimate from current predictions, no retrain: merge reaction+anecdote -> 17/33 correct, explainer+anecdote -> 15/33, today 13/33. Report 6-label and merged scores; keep 0.60 target.
- Train: run takemeter.ipynb sections 1–5 and save the model (step 0 of PLAN.md).
- Write criteria.md (5 criteria, before any deploy run).
- Build app.py with JSONL logging and deploy to an HF Space.

## Decisions
- 2026-11-18: Live browser demo on GitHub Pages: https://jasonjosephit.github.io/ai201-project5-takemeter/ (docs/index.html, plain fetch to the Space /classify API; Space CORS allows the github.io origin).
- 2026-11-18: max_length raised 128 -> 512 (4x, DistilBERT max), retrained (seed 42, 10 epochs) and redeployed. Test acc 0.30 -> 0.39, macro-F1 0.28 -> 0.36. Posts cut: 34% -> 5% (10/215). Longest post (1120 tokens) takes 237 ms server-side. 128 model kept locally in model_128/ and on Hub at revision 40417fc. No before-trials were run at 128, so trials will be at 512.
- 2026-11-18: Criteria: #3 warm latency median <= 300 ms; #5 split into 5a hosted matches local >= 19/20 and 5b macro-F1 >= 0.60 (kept knowing current model is 0.28); added #6 advertisement precision >= 0.70 on test split. #7 added: log n_tokens + truncated, must match local count 20/20. criteria.md written; app redeployed with the new fields.
- 2026-11-11: Project 5 extension = shape A (deploy and instrument), Path A (hosted on a Hugging Face Space with Gradio). Extra credit = per-stage latency breakdown. Out of scope: new labels, hardening, auth, UI polish. Plan in PLAN.md / PLAN.html.
- 2026-10-26: Added `advertisement` as a 6th label (step 0: is it selling something the writer is connected to?), kept `explainer` as the catch-all. find_ads.py collects 35 ads; existing 180 rows untouched.
- 2026-10-26: Taxonomy written (Milestone 2) in Project 3 README + label_definitions.txt: three ordered questions (position? → lived it? → else explainer) make labels mutually exclusive. Hardest boundary: analysis vs explainer. Label ids stay analysis/hot_take/reaction/explainer/anecdote.
- 2026-10-26: Jev (TypeSafe) is used only for the first-pass labels; training is the notebook's DistilBERT.
- 2026-10-26: Balance to ~35 per label (about 175 rows), keeping 40 of the 136 explainers.
- 2026-10-26: Text is the real post (title + body, or title only for link posts), not the summaries, so the model can't learn summary style as a label cue.
- 2026-10-26: More posts come from the Arctic Shift archive, because Reddit's API blocks this machine.

## Open items / waiting on
- Milestone 3: criteria.md still blank.
- README pre-labelling disclosure.

## Idea Shelf
- 2026-11-11: URL intake (paste a Reddit URL, a script pulls title + body via Arctic Shift by post id, then labels it). Candidate for the extra-credit second improvement; needs a URL criterion written before any run.
