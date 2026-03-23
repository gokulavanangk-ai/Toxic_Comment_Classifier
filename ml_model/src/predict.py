import torch
import os
import joblib
import logging
import sys
from typing import List, Union

from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_loader import clean_text


# =============================
# CONFIG
# =============================

MODEL_DIR = "model_output"
MAX_LEN = 192

THRESHOLDS = {
    "severe_toxic": 0.85,
    "toxic": 0.70
}

# =============================
# LOGGING
# =============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================
# PREDICTOR CLASS
# =============================

class ToxicityPredictor:

    def __init__(self, model_dir: str = MODEL_DIR):

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Inference device: {self.device}")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
            self.model.to(self.device)
            self.model.eval()

            le_path = os.path.join(model_dir, "label_encoder.joblib")
            self.label_encoder = joblib.load(le_path)
            self.labels = list(self.label_encoder.classes_)

            logger.info("Model, tokenizer, and label encoder loaded successfully.")

        except Exception as e:
            logger.error(f"Failed to load model resources: {e}")
            raise


    # =============================
    # CORE PREDICTION LOGIC
    # =============================

    def _apply_thresholds(self, scores):

        top_idx = scores.argmax()
        top_label = self.labels[top_idx]
        confidence = float(scores[top_idx])

        final_label = "review"

        if top_label == "severe_toxic" and confidence >= THRESHOLDS["severe_toxic"]:
            final_label = "severe_toxic"

        elif top_label == "toxic" and confidence >= THRESHOLDS["toxic"]:
            final_label = "toxic"

        elif top_label == "non_toxic":
            final_label = "non_toxic"

        return final_label, top_label, confidence


    def predict(self, text: str) -> dict:

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text must be a non-empty string.")

        cleaned_text = clean_text(text)

        inputs = self.tokenizer(
            cleaned_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=MAX_LEN
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        scores = probs.cpu().numpy()[0]

        final_label, raw_label, confidence = self._apply_thresholds(scores)

        score_dict = {
            label: float(score)
            for label, score in zip(self.labels, scores)
        }

        return {
            "text": text,
            "cleaned_text": cleaned_text,
            "prediction": final_label,
            "raw_prediction": raw_label,
            "confidence": confidence,
            "scores": score_dict
        }


    # =============================
    # BATCH PREDICTION
    # =============================

    def predict_batch(self, texts: List[str]) -> List[dict]:

        if not isinstance(texts, list) or not texts:
            raise ValueError("Input must be a non-empty list of strings.")

        cleaned_texts = [clean_text(t) for t in texts]

        inputs = self.tokenizer(
            cleaned_texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=MAX_LEN
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        results = []

        for i, scores in enumerate(probs.cpu().numpy()):

            final_label, raw_label, confidence = self._apply_thresholds(scores)

            score_dict = {
                label: float(score)
                for label, score in zip(self.labels, scores)
            }

            results.append({
                "text": texts[i],
                "cleaned_text": cleaned_texts[i],
                "prediction": final_label,
                "raw_prediction": raw_label,
                "confidence": confidence,
                "scores": score_dict
            })

        return results


# =============================
# TEST BLOCK
# =============================

if __name__ == "__main__":

    predictor = ToxicityPredictor()

    test_texts = [
        "Unakku arive illaya?",
        "You are a very good person.",
        "Nee oru loosu",
        "Enda ipdi panra?",
        "This is a wonderful place.",
        "k1ll urself",
        "nee saavu da 😂",
        "People like you ruin everything.",
        "I strongly disagree with your opinion."
    ]

    print("\n" + "=" * 60)
    print("Production Inference Test")
    print("=" * 60)

    for result in predictor.predict_batch(test_texts):
        print(f"\nInput: {result['text']}")
        print(f"Final Prediction: {result['prediction']}")
        print(f"Raw Prediction: {result['raw_prediction']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Scores: {result['scores']}")

    print("\n" + "=" * 60)