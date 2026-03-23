import os
import sys
import time
import logging
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from logging.handlers import RotatingFileHandler

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.predict import ToxicityPredictor


# ============================
# CONFIG
# ============================

MODEL_DIR = "model_output"
MAX_INPUT_CHARS = 500
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

API_LOG_FILE = os.path.join(LOG_DIR, "api.log")

# Rate limit: 30 requests per minute per IP
RATE_LIMIT = "30/minute"


# ============================
# LOGGING SETUP
# ============================

logger = logging.getLogger("toxicity_api")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    API_LOG_FILE,
    maxBytes=10_000_000,
    backupCount=5,
    encoding="utf-8"
)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# ============================
# FASTAPI INIT
# ============================

app = FastAPI(
    title="Toxic Content Classifier API",
    version="2.0.0"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# ============================
# EXCEPTION HANDLERS
# ============================

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================
# MODEL LOADING
# ============================

predictor = None

@app.on_event("startup")
def load_model():
    global predictor
    logger.info("Loading model...")
    predictor = ToxicityPredictor(MODEL_DIR)
    logger.info("Model loaded successfully.")


# ============================
# REQUEST / RESPONSE MODELS
# ============================

class TextRequest(BaseModel):
    text: str

    @validator("text")
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Text must be non-empty.")
        if len(v) > MAX_INPUT_CHARS:
            raise ValueError("Input too long.")
        return v.strip()


class PredictionResponse(BaseModel):
    prediction: str
    raw_prediction: str
    confidence: float
    process_time_ms: float
    timestamp: str


# ============================
# ENDPOINTS
# ============================

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def readiness():
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    return {"status": "ready"}


@app.post("/predict", response_model=PredictionResponse)
@limiter.limit(RATE_LIMIT)
def predict(request: Request, payload: TextRequest):

    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not ready")

    start_time = time.time()

    result = predictor.predict(payload.text)

    process_time = (time.time() - start_time) * 1000
    timestamp = datetime.utcnow().isoformat()

    # Structured logging (NO RAW TEXT)
    logger.info(
        
        f"prediction={result['prediction']} "
        f"confidence={round(result['confidence'],4)} "
        f"time_ms={round(process_time,2)}"
    )

    return {
        "original_comment" : payload.text,
        "prediction": result["prediction"],
        "raw_prediction": result["raw_prediction"],
        "confidence": round(result["confidence"], 4),
        "process_time_ms": round(process_time, 2),
        "timestamp": timestamp
    }


# ============================
# LOCAL RUN (DEV ONLY)
# ============================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000)