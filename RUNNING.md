# Running TakeMeter

## Where it runs

| | |
|---|---|
| App + API | https://huggingface.co/spaces/JasonJosephIT/takemeter |
| API endpoint | `POST https://jasonjosephit-takemeter.hf.space/gradio_api/call/classify` |
| Demo page | https://jasonjosephit.github.io/ai201-project5-takemeter/ |
| Model | https://huggingface.co/JasonJosephIT/takemeter (512 tokens; the 128-token model is revision `40417fc`) |
| Platform | Hugging Face Spaces, Gradio SDK, `cpu-basic`, needs HF PRO |

## Call the API

```bash
EVENT=$(curl -s -X POST https://jasonjosephit-takemeter.hf.space/gradio_api/call/classify \
  -H "Content-Type: application/json" \
  -d '{"data": ["Anyone know a good dentist near Winter Park?"]}' | python3 -c "import sys,json;print(json.load(sys.stdin)['event_id'])")
curl -s https://jasonjosephit-takemeter.hf.space/gradio_api/call/classify/$EVENT
```

The second call returns `event: complete` and a `data:` line with the label and six confidences.
Send the post's text, not a link.

## Set up locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install torch transformers datasets scikit-learn pandas "huggingface-hub>=0.34,<1.0" requests
hf auth login        # token with Write access
```

Do not install `gradio_client` into this environment: it upgrades `huggingface-hub` past what
`transformers` accepts and breaks local training.

## Train

```bash
EPOCHS=10 python train_save.py
```

Uses `labels.csv`, seed 42, a stratified 70/15/15 split and `max_length` 512. Writes `./model` and
`test_split.csv`. About 1 minute on Apple Silicon. With the default 3 epochs, the model predicts one
label for everything.

## Deploy

```bash
hf upload JasonJosephIT/takemeter model .                                   # model weights
hf upload JasonJosephIT/takemeter space . --repo-type space                 # app.py, requirements.txt, README.md
```

The Space rebuilds on upload; it shows **Running** after 3–4 minutes. The first-time setup was
`hf repo create JasonJosephIT/takemeter --repo-type space --space_sdk gradio`.

To serve the 128-token model, set `MAX_LENGTH = 128` in `space/app.py` and pass
`revision="40417fc2c33fd851535fb6382693f77ebb16c5df"` to both `from_pretrained` calls.

## Run the trials

```bash
python trials.py                                                   # 512 model, writes run_log.json
python trials.py --model-dir model_128 --max-length 128 --out run_log_128.json
```

3 warm trials (35 requests each) and 3 cold starts. The cold trials pause and restart the Space,
so it is unavailable for about 15 s each time. Takes about 5 minutes.

## Read the logs

Each request prints one JSON line to the Space's **Logs** tab
(https://huggingface.co/spaces/JasonJosephIT/takemeter?logs=container). The lines are lost when the
Space restarts.

## Demo page

`docs/index.html`, served by GitHub Pages from `main` / `docs`. Push to `main` and it updates in
about a minute. Wake the Space a minute before a live demo.
