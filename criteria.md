# TakeMeter (Project 5): acceptance criteria

Written 2026-11-18, before any trial run. Shape A (deploy and instrument), Path A
(Hugging Face Space, Gradio, `cpu-basic`). Space: https://huggingface.co/spaces/JasonJosephIT/takemeter

Criteria 1–4, 5a and 7 test the deployment. 5b and 6 test the model's output.
Unless stated, a "trial" is one batch of requests sent with `curl` to the `/classify`
endpoint, and every criterion is run 3 times.

---

## 1. Reachable (extension)

The Space URL returns a label and a confidence for a 50-word post within 5 s, on a warm
Space, in 3/3 trials.

**Why this target:** 5 s is the longest a person waits on a single text box before
assuming it broke. The first warm checks took 0.4–0.6 s round trip, so 5 s leaves room
for slow networks, but a hung or crashed Space still fails it.

## 2. Logged (extension)

Every request writes one JSON line with `ts`, `input`, `label`, `confidence`,
`latency_ms`, `t_tokenize_ms`, `t_model_ms`, `t_post_ms`, `n_tokens` and `truncated`.
10/10 requests logged per trial, 0 missing fields, in 3/3 trials.

**Why this target:** the log is the only record of what real users send, and the
latency and truncation criteria are read from it. A single lost line means I cannot
trust counts taken from it, so the target is all of them, not most.

## 3. Warm latency (extension)

Median server-side `latency_ms` is at most 300 ms over 20 requests, in 3/3 trials.

**Why this target:** the first warm requests took 31–35 ms on free CPU, with one
417 ms outlier right after start-up. 300 ms is fast enough to feel instant, sits below
that outlier, and leaves room for longer posts and a busy shared CPU. The median is
used so one slow request does not decide the result.

## 4. Cold start (extension)

After the Space has gone to sleep, the first request answers within 60 s, in 3/3 trials.

**Why this target:** a sleeping Space has to rebuild, download the 255 MB model and
load it before it can answer. 60 s is the most a visitor to a hosted page would wait
with a loading message; past that it looks dead.

## 5a. Hosted matches local (extension)

On 20 posts from `test_split.csv`, the hosted label equals the local `./model` label on
at least 19/20.

**Why this target:** this checks the model survived the upload unchanged (same
weights, tokenizer and 128-token cut). One mismatch is allowed for float
differences between Apple Silicon (MPS) and the Space's CPU when two labels are
nearly tied, which is likely with confidences around 0.27.

## 5b. Model quality (system)

Macro-F1 at least 0.60 on the 33-post held-out test split.

**Why this target:** 0.60 is where six labels become useful for sorting a feed,
roughly three times the 0.17 of random guessing. The deployed model scores 0.28
(`advertisement` 0.73, `anecdote` and `hot_take` 0.00), so I expect to miss this. The
target stays as written: the miss gets a diagnosis, not a lower number.

## 6. Advertisement precision (system)

`advertisement` precision at least 0.70 on the held-out test split.

**Why this target:** a false ad hides a real post from a reader, so being wrong
about ads costs more than missing one. The current model has 0.80 (4 of 5 ad calls
correct). After the Project 3 relabel, precision fell to 0.44 on one seed, with
anecdotes and analyses called ads; 0.70 catches that drift. With 6 ads in the test
split, one extra false ad moves precision by about 0.13, so 0.70 allows one.

## 7. Input truncation is visible (extension)

Every log line records `n_tokens` (full token count) and `truncated`
(`n_tokens > 128`). On 20 posts from `test_split.csv`, both match a local tokenizer
count on 20/20.

**Why this target:** the model reads only the first 128 tokens. 34% of the 215 posts
are longer (77% of `analysis`, 49% of `advertisement`), and Project 3's diagnosis was
that the deciding cue often sits past the cut. Without these fields the cut is
invisible; with them, wrong answers can be checked against truncation, and the
`max_length` 256 improvement can be measured. It is a count, so the target is exact.

**Revised 2026-11-18, before any trial:** `truncated` is `n_tokens > MAX_LENGTH`,
where `MAX_LENGTH` is now 512 (4 × 128, DistilBERT's maximum), not 128.
**Why revised:** the token limit was raised and the model retrained before trials
started, so the flag follows the deployed limit. 10 of 215 posts (5%) are still
longer than 512. The target (20/20 match) is unchanged.

<!--
Revisions go underneath the original line, never in place of it.
Lowering a target because it was missed is not a revision.
-->
