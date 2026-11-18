"""Train TakeMeter with the notebook's settings (seed 42) and save it to ./model.

Same split, labels and hyperparameters as takemeter.ipynb sections 2-5, so the saved
model matches what the notebook would produce. Run: python train_save.py
"""
import json

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, Trainer,
                          TrainingArguments, set_seed)

LABELS = ["analysis", "hot_take", "reaction", "explainer", "anecdote", "advertisement"]
BASE_MODEL = "distilbert-base-uncased"
import os
EPOCHS = int(os.environ.get("EPOCHS", 3))
LEARNING_RATE, BATCH_SIZE, MAX_LENGTH, SEED = 2e-5, 16, 128, 42

df = pd.read_csv("labels.csv")
df["label"] = df["label"].astype(str).str.strip()

rest, test = train_test_split(df, test_size=0.15, random_state=SEED, stratify=df["label"])
train, val = train_test_split(rest, test_size=0.15 / 0.85, random_state=SEED, stratify=rest["label"])
test.to_csv("test_split.csv", index=False)

set_seed(SEED)
tok = AutoTokenizer.from_pretrained(BASE_MODEL)
model = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL, num_labels=len(LABELS),
    id2label=dict(enumerate(LABELS)), label2id={l: i for i, l in enumerate(LABELS)},
)
lookup = {l: i for i, l in enumerate(LABELS)}


def to_ds(frame):
    ds = Dataset.from_pandas(pd.DataFrame({"text": frame["text"].astype(str),
                                           "labels": frame["label"].map(lookup)}))
    return ds.map(lambda b: tok(b["text"], truncation=True, padding="max_length",
                                max_length=MAX_LENGTH), batched=True)


def metrics(p):
    pred = np.argmax(p.predictions, axis=-1)
    return {"accuracy": accuracy_score(p.label_ids, pred),
            "f1_macro": f1_score(p.label_ids, pred, average="macro", zero_division=0)}


trainer = Trainer(
    model=model,
    args=TrainingArguments(output_dir="./takemeter_out", num_train_epochs=EPOCHS,
                           learning_rate=LEARNING_RATE, per_device_train_batch_size=BATCH_SIZE,
                           per_device_eval_batch_size=BATCH_SIZE, eval_strategy="epoch",
                           save_strategy="no", logging_steps=10, seed=SEED, report_to="none"),
    train_dataset=to_ds(train), eval_dataset=to_ds(val), compute_metrics=metrics,
)
trainer.train()

result = trainer.evaluate(to_ds(test))
print(json.dumps({"test_accuracy": result["eval_accuracy"], "test_f1_macro": result["eval_f1_macro"]}))

trainer.save_model("model")
tok.save_pretrained("model")
print("Saved to ./model")
