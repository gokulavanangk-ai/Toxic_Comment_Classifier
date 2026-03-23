# Code-Mixed Toxic Content Classifier

Production-ready Transformer-based NLP system for detecting toxic content in:

* **Tamil**
* **English**
* **Tanglish** (Tamil in Latin script)

Built using **MuRIL (google/muril-base-cased)** fine-tuned for 3-class toxicity classification:

* `non_toxic`
* `toxic`
* `severe_toxic`

Designed for real-world deployment with rate limiting, logging, thresholding, and load testing support.

---

# 📦 Project Structure

```
/
├── model_output/           # Trained model, tokenizer, label encoder
├── logs/                   # JSONL prediction logs
├── src/
│   ├── api.py              # Production FastAPI server (rate-limited, logged)
│   ├── data_loader.py      # Hardened dataset loader & cleaner
│   ├── predict.py          # Inference engine with threshold logic
│   └── train_muril.py      # Production training pipeline
├── locustfile.py           # Load testing configuration
├── requirements.txt
├── README.md
└── *.csv                   # Structured datasets (tamil.csv, english.csv, tanglish.csv)
```

---

# 🧠 Model Overview

* Base Model: `google/muril-base-cased`
* Architecture: Transformer (BERT-style sequence classification)
* Classes:

  * non_toxic
  * toxic
  * severe_toxic
* Max token length: 192
* Confidence thresholding enabled
* Near-duplicate removal during preprocessing
* Stratified train/validation split
* Macro-F1 monitored during training

---

# 📊 Dataset Structure

Each CSV file must contain:

```
text,label
```

Example:

```
nee saavu da,severe_toxic
I disagree with you,non_toxic
you are useless,toxic
```

Requirements:

* UTF-8 or UTF-16 encoding supported
* No empty rows
* No duplicate sentences
* Clear label boundaries

---

# ⚙️ Setup

## 1️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Windows:

```bash
.\venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Optional (recommended):

Set HuggingFace token for stable downloads:

```bash
set HF_TOKEN=your_token   # Windows
export HF_TOKEN=your_token  # Linux/Mac
```

---

# 🏋️ Training

Train model:

```bash
python src/train_muril.py --epochs 5 --batch_size 16
```

Output saved to:

```
model_output/
```

Training includes:

* Dataset audit logging
* Label distribution validation
* Stratified split
* Macro F1 tracking
* Best model checkpoint restore
* Label encoder persistence

---

# 🧪 CLI Inference Test

```bash
python src/predict.py
```

Verifies:

* Model loads
* Threshold logic applied
* Batch inference works

---

# 🚀 Run Production API

### Windows (single worker recommended)

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Open Swagger UI:

```
http://localhost:8000/docs
```

---

# 🔌 API Endpoints

## Health Check

```
GET /health
```

Returns service health.

---

## Readiness Probe

```
GET /ready
```

Returns 200 only if model loaded and ready.

---

## Predict

```
POST /predict
```

### Request

```json
{
  "text": "nee saavu da 😂"
}
```

### Response

```json
{
  "prediction": "severe_toxic",
  "raw_prediction": "severe_toxic",
  "confidence": 0.9867,
  "process_time_ms": 64.03,
  "timestamp": "2026-02-22T13:49:24.019Z"
}
```

---

# 🛡️ Production Safeguards

* Rate limiting enabled (per IP)
* Structured JSONL logging
* Confidence threshold enforcement
* Input validation
* Cleaned text normalization
* Graceful startup and shutdown
* No model reload per request
* Lazy model initialization

---

# 📈 Load Testing (Locust)

Create `locustfile.py`:

```python
from locust import HttpUser, task, between
import random

texts = [
    "nee saavu da 😂",
    "You are useless",
    "I disagree with you",
    "k1ll urself",
    "This is fine"
]

class ToxicityUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def predict(self):
        self.client.post(
            "/predict",
            json={"text": random.choice(texts)}
        )
```

Run:

```bash
locust
```

Open:

```
http://localhost:8089
```

Test capacity:

* Start with 20 users
* Increase gradually
* Monitor latency & failure %

---

# 📊 Performance (CPU, Single Worker)

Expected:

* 60–120ms average latency
* ~10–15 RPS stable
* 0% failure under safe load

High concurrency requires:

* Linux
* Gunicorn workers
* Possibly GPU acceleration

---

# ⚠ Known Limitations

* Windows multi-worker mode unstable
* Single-process inference bound by CPU
* Severe vs toxic boundary sensitive to dataset
* Confidence not temperature-calibrated

---

# 📌 Deployment Recommendations

For real production:

* Deploy on Linux
* Use Gunicorn + Uvicorn workers
* Reverse proxy (Nginx)
* Enable HTTPS
* Add monitoring (Prometheus/Grafana)
* Add structured metrics endpoint
* Implement request tracing

---

# 🧪 Monitoring

Logs stored in:

```
logs/predictions.jsonl
```

Each entry contains:

* timestamp
* text
* prediction
* confidence
* latency

---

# 📎 Version

- API Version: 1.1.0
- Model: MuRIL fine-tuned (custom dataset)