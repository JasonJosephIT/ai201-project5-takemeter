---
status: active
progress: Space live and logging; next is criteria.md + trials
next_date:
updated: 2026-11-18
---

## Now
- 2026-11-18: LIVE at https://huggingface.co/spaces/JasonJosephIT/takemeter (HF PRO, cpu-basic). API endpoint is /classify (Gradio names it after the function). 3 test calls logged with stage timings; server latency 31-417 ms, round trip 375-589 ms. Logs only in Space Logs tab + ephemeral requests.jsonl (no CommitScheduler yet). Model: huggingface.co/JasonJosephIT/takemeter.
labels.csv final: 215 rows (40 explainer, 35 each of the other five), reviewed and confirmed by me. Copied to the Project 3 repo.

## Next
- Train: run takemeter.ipynb sections 1–5 and save the model (step 0 of PLAN.md).
- Write criteria.md (5 criteria, before any deploy run).
- Build app.py with JSONL logging and deploy to an HF Space.

## Decisions
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
