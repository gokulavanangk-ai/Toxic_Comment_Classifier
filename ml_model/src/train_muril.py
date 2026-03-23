import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import logging
import argparse
import numpy as np
import random

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)

from torch.utils.data import Dataset
import torch.nn as nn

from src.data_loader import load_and_preprocess_data

# =============================
# CONFIG
# =============================

MODEL_NAME = "google/muril-base-cased"
MAX_LEN = 192
OUTPUT_DIR = "model_output"
SEED = 42

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# =============================
# REPRODUCIBILITY
# =============================

def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# =============================
# DATASET CLASS
# =============================

class ToxicDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


# =============================
# METRICS
# =============================

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="macro", zero_division=0
    )

    acc = accuracy_score(labels, preds)

    return {
        "accuracy": acc,
        "macro_f1": f1,
        "macro_precision": precision,
        "macro_recall": recall
    }


# =============================
# WEIGHTED TRAINER
# =============================

class WeightedTrainer(Trainer):
    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")

        loss_fct = nn.CrossEntropyLoss(
            weight=self.class_weights.to(logits.device)
        )

        loss = loss_fct(
            logits.view(-1, model.config.num_labels),
            labels.view(-1)
        )

        return (loss, outputs) if return_outputs else loss

# =============================
# TRAIN FUNCTION
# =============================

def train_model(
    data_path=".",
    epochs=5,
    train_batch_size=16,
    eval_batch_size=16,
    smoke_test=False
):

    set_seed()

    logger.info("Loading dataset...")
    df = load_and_preprocess_data(data_path, augment=False)

    # Safety check
    logger.info(f"Total rows: {len(df)}")
    logger.info(f"Unique cleaned: {df['cleaned_text'].nunique()}")
    logger.info(f"Label distribution:\n{df['label'].value_counts()}")

    if len(df) < 2000:
        raise ValueError("Dataset too small for transformer training.")

    # Label encoding
    le = LabelEncoder()
    df["label_encoded"] = le.fit_transform(df["label"])

    # Save label encoder later
    num_labels = len(le.classes_)

    # Split
    X_train, X_val, y_train, y_val = train_test_split(
        df["cleaned_text"].tolist(),
        df["label_encoded"].tolist(),
        test_size=0.2,
        stratify=df["label_encoded"],
        random_state=SEED
    )

    if smoke_test:
        logger.warning("Running smoke test mode")
        X_train, y_train = X_train[:100], y_train[:100]
        X_val, y_val = X_val[:30], y_val[:30]
        epochs = 1

    logger.info(f"Training samples: {len(X_train)}")
    logger.info(f"Validation samples: {len(X_val)}")

    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_encodings = tokenizer(
        X_train,
        truncation=True,
        padding=True,
        max_length=MAX_LEN
    )

    val_encodings = tokenizer(
        X_val,
        truncation=True,
        padding=True,
        max_length=MAX_LEN
    )

    train_dataset = ToxicDataset(train_encodings, y_train)
    val_dataset = ToxicDataset(val_encodings, y_val)

    # Model
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels
    )

    # Class weights
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(df["label_encoded"]),
        y=df["label_encoded"]
    )

    class_weights = torch.tensor(class_weights, dtype=torch.float)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=epochs,
        per_device_train_batch_size=train_batch_size,
        per_device_eval_batch_size=eval_batch_size,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        weight_decay=0.01,
        warmup_steps=100,
        logging_steps=20,
        save_total_limit=2,
        seed=SEED,
        fp16=torch.cuda.is_available(),
        report_to=[]
    )

    trainer = WeightedTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        class_weights=class_weights,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )

    logger.info("Starting training...")
    trainer.train()

    logger.info("Saving model...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    import joblib
    joblib.dump(le, os.path.join(OUTPUT_DIR, "label_encoder.joblib"))

    logger.info("Training complete. Model saved.")


# =============================
# ENTRYPOINT
# =============================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--smoke_test", action="store_true")
    args = parser.parse_args()

    train_model(
        epochs=args.epochs,
        train_batch_size=args.batch_size,
        smoke_test=args.smoke_test
    )