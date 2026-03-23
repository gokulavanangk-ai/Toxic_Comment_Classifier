import pandas as pd
import re
import os
import logging
import unicodedata
import random
from typing import List, Tuple
from difflib import SequenceMatcher
from collections import Counter

# ===========================
# CONFIG
# ===========================

DATA_FILES = ["tamil.csv", "english.csv", "tanglish.csv"]
SUPPORTED_ENCODINGS = [
    "utf-8-sig",   # <-- add this FIRST
    "utf-16",
    "utf-16le",
    "utf-8",
    "latin1"
]

SIMILARITY_THRESHOLD = 0.97
MAX_TEXT_LENGTH = 512
ENABLE_AUGMENTATION = True
AUGMENT_MULTIPLIER = 2  # per toxic sample
TARGET_NON_TOXIC_RATIO = 0.7  # realistic production skew


# ===========================
# LOGGING
# ===========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ===========================
# FILE READING
# ===========================

def read_csv_with_fallback(file_path: str):
    for enc in SUPPORTED_ENCODINGS:
        try:
            df = pd.read_csv(
                file_path,
                sep="\t",          # force tab
                encoding=enc,
                engine="python"
            )
            logger.info(f"Read {file_path} with encoding {enc}")
            return df
        except Exception as e:
            logger.warning(f"Encoding {enc} failed: {e}")
            continue

    raise ValueError(f"Could not read {file_path}")
# ===========================
# NORMALIZATION LAYER
# ===========================

def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def normalize_repetitions(text: str) -> str:
    # loooosu → loosu
    return re.sub(r"(.)\1{2,}", r"\1\1", text)


def reverse_leetspeak(text: str) -> str:
    mapping = {
        "0": "o",
        "1": "i",
        "3": "e",
        "@": "a",
        "$": "s",
        "!": "i"
    }
    return "".join(mapping.get(c, c) for c in text)


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = normalize_unicode(text)
    text = text.lower()
    text = reverse_leetspeak(text)

    text = re.sub(r"http\S+", " URL ", text)
    text = re.sub(r"@\w+", " USER ", text)

    text = normalize_repetitions(text)

    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]

    return text


# ===========================
# NEAR DUPLICATE REMOVAL
# ===========================

def is_similar(a: str, b: str, threshold: float = SIMILARITY_THRESHOLD) -> bool:
    if abs(len(a) - len(b)) > 10:
        return False
    return SequenceMatcher(None, a, b).ratio() > threshold


def remove_near_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    texts = df["cleaned_text"].tolist()
    keep_indices = []

    for i, text in enumerate(texts):
        duplicate_found = False
        for j in keep_indices:
            if is_similar(text, texts[j]):
                duplicate_found = True
                break
        if not duplicate_found:
            keep_indices.append(i)

    return df.iloc[keep_indices].reset_index(drop=True)


# ===========================
# ADVERSARIAL AUGMENTATION
# ===========================

def random_case(text: str) -> str:
    return "".join(
        c.upper() if random.random() > 0.5 else c.lower() for c in text
    )


def insert_punctuation(text: str) -> str:
    if len(text) < 3:
        return text
    pos = random.randint(1, len(text) - 2)
    return text[:pos] + "." + text[pos:]


def char_drop(text: str) -> str:
    if len(text) < 4:
        return text
    pos = random.randint(0, len(text) - 1)
    return text[:pos] + text[pos+1:]


def generate_adversarial_variants(text: str) -> List[str]:
    variants = []
    transforms = [random_case, insert_punctuation, char_drop]

    for _ in range(AUGMENT_MULTIPLIER):
        t = random.choice(transforms)
        variants.append(t(text))

    return variants


def augment_dataset(df: pd.DataFrame) -> pd.DataFrame:
    augmented_rows = []

    for _, row in df.iterrows():
        if row["label"] in ["toxic", "severe_toxic"]:
            variants = generate_adversarial_variants(row["cleaned_text"])
            for v in variants:
                augmented_rows.append({
                    "text": v,
                    "label": row["label"],
                    "cleaned_text": clean_text(v)
                })

    if augmented_rows:
        df_aug = pd.DataFrame(augmented_rows)
        df = pd.concat([df, df_aug], ignore_index=True)

    return df


# ===========================
# CLASS REBALANCING
# ===========================

def rebalance_classes(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["label"].value_counts().to_dict()

    non_toxic_df = df[df["label"] == "non_toxic"]
    toxic_df = df[df["label"] != "non_toxic"]

    desired_non_toxic = int(len(df) * TARGET_NON_TOXIC_RATIO)

    if len(non_toxic_df) > desired_non_toxic:
        non_toxic_df = non_toxic_df.sample(desired_non_toxic, random_state=42)

    df = pd.concat([non_toxic_df, toxic_df]).sample(frac=1, random_state=42)

    return df.reset_index(drop=True)


# ===========================
# MAIN PIPELINE
# ===========================

def load_and_preprocess_data(base_path: str = ".", augment: bool = True) -> pd.DataFrame:
    dfs = []
    for filename in DATA_FILES:
        file_path = os.path.join(base_path, filename)
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            continue

        df = read_csv_with_fallback(file_path)

        df.columns = ["text", "label"] + list(df.columns[2:])
        df = df[["text", "label"]]

        dfs.append(df)
        logger.info(f"Loaded {filename}: {df.shape[0]} rows")

    if not dfs:
        raise ValueError("No dataset files loaded.")

    df = pd.concat(dfs, ignore_index=True)

    logger.info(f"Initial rows: {len(df)}")

    df.dropna(subset=["text", "label"], inplace=True)
    df.drop_duplicates(subset=["text"], inplace=True)

    df["cleaned_text"] = df["text"].apply(clean_text)
    df = df[df["cleaned_text"] != ""]

    logger.info(f"After basic cleaning: {len(df)}")

    df = remove_near_duplicates(df)
    logger.info(f"After near-duplicate removal: {len(df)}")

    if augment and ENABLE_AUGMENTATION:
        df = augment_dataset(df)
        logger.info(f"After augmentation: {len(df)}")
        df = rebalance_classes(df)

    logger.info("Final label distribution:")
    logger.info(df["label"].value_counts())

    return df


# ===========================
# SMOKE TEST
# ===========================

if __name__ == "__main__":
    df = load_and_preprocess_data(".", augment=False)
    print(df.sample(5))