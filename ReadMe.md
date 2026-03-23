# 🛡️ Toxic Comment Classifier

> An end-to-end AI-powered web application that detects and classifies toxic comments in real time using Machine Learning and Natural Language Processing.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Purpose & Motivation](#purpose--motivation)
- [Project Impact](#project-impact)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Feasibility & Limitations](#feasibility--limitations)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

The **Toxic Comment Classifier** is a full-stack machine learning application that automatically identifies harmful, abusive, or toxic content in user-submitted text. It combines a trained NLP model with a REST API backend and an interactive frontend to deliver real-time toxicity predictions.

Whether you are building a community platform, a social media app, or a moderation tool — this project provides a ready-to-integrate pipeline for automated content safety.

---

## Purpose & Motivation

Online platforms face a growing challenge: toxic, abusive, and harassing comments degrade user experience, silence voices, and force communities to shut down open discussion. Manual moderation is slow, inconsistent, and difficult to scale.

This project addresses that problem by building an **automated, ML-driven toxicity detection system** that:

- Classifies text as **toxic or non-toxic** in real time
- Provides a clean API that can be integrated into any platform
- Enables developers to add content moderation without relying on third-party paid services

---

## Project Impact

| Impact Area | Description |
|---|---|
| 🧑‍🤝‍🧑 **Community Safety** | Protects users from harassment, hate speech, and abusive language online |
| ⚡ **Real-time Moderation** | Enables instant flagging or filtering of harmful content at scale |
| 💰 **Cost Efficiency** | Open-source alternative to expensive commercial moderation APIs |
| 🌐 **Platform Agnostic** | REST API design allows integration with any web, mobile, or desktop app |
| 🔬 **Research Value** | Provides a reusable NLP pipeline for toxicity research and academic study |
| 🧠 **Bias Awareness** | Highlights the importance of responsible AI in handling sensitive language tasks |

---

## Tech Stack

### Machine Learning
- **Python** — core language for model development
- **Jupyter Notebook** — exploratory data analysis, model training and evaluation
- **Scikit-learn / TensorFlow / Keras** — ML model building and training
- **NLP libraries** — text preprocessing, tokenization, vectorization (TF-IDF / embeddings)

### Backend
- **Python** — server-side logic
- **Flask / FastAPI** — REST API for serving predictions

### Frontend
- **JavaScript** — interactive UI logic
- **HTML / CSS** — layout and styling

---

## Project Structure

```
Toxic_Comment_Classifier/
│
├── ml_model/               # ML pipeline: data, notebooks, trained model artifacts
│   ├── *.ipynb             # Jupyter notebooks for EDA, training, evaluation
│   └── ...
│
├── backend/                # Python REST API for serving predictions
│   ├── app.py / main.py    # API entry point
│   ├── model_loader.py     # Loads trained model for inference
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Web interface for user interaction
│   ├── index.html          # Main HTML page
│   ├── script.js           # Frontend logic
│   └── style.css           # Styling
│
├── .gitignore
└── ReadMe.md
```

---

## How It Works

```
User Input (text)
      │
      ▼
  Frontend UI  ──── HTTP POST ────▶  Backend API
                                         │
                                         ▼
                                   Text Preprocessing
                                   (cleaning, tokenization)
                                         │
                                         ▼
                                   ML Model Inference
                                         │
                                         ▼
                                   Prediction Result
                                   (Toxic / Non-Toxic)
                                         │
      ◀──── JSON Response ──────────────┘
      │
      ▼
  Display Result to User
```

1. The user types or pastes a comment into the web interface.
2. The frontend sends the text to the backend via a REST API call.
3. The backend preprocesses the text and runs it through the trained ML model.
4. The model returns a prediction: **Toxic** or **Non-Toxic** (with confidence score).
5. The result is displayed to the user on the frontend.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js (for frontend, if applicable)
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/gokulavanangk-ai/Toxic_Comment_Classifier.git
cd Toxic_Comment_Classifier
```

### 2. Set Up the ML Model

```bash
cd ml_model
# Open and run the Jupyter notebooks to train and export the model
jupyter notebook
```

### 3. Start the Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The API will be running at `http://localhost:5000` (or your configured port).

### 4. Launch the Frontend

Open `frontend/index.html` in your browser, or serve it with a local HTTP server:

```bash
cd frontend
python -m http.server 8080
```

Then visit `http://localhost:8080` in your browser.

---

## API Reference

### `POST /predict`

Classifies a given comment as toxic or non-toxic.

**Request Body:**
```json
{
  "comment": "Your comment text here"
}
```

**Response:**
```json
{
  "prediction": "toxic",
  "confidence": 0.92
}
```

---

## Feasibility & Limitations

### ✅ Feasibility

- The project uses well-established NLP techniques (TF-IDF, embeddings) that are proven to work well for text classification tasks.
- The full-stack architecture (ML + API + UI) is modular and easy to extend or replace individual components.
- Lightweight enough to run locally without GPU infrastructure.
- The REST API design makes it straightforward to integrate into production applications.

### ⚠️ Limitations

| Limitation | Details |
|---|---|
| **Context Blindness** | The model classifies individual comments and may miss context-dependent toxicity (e.g., sarcasm) |
| **Language Scope** | Primarily trained on English-language data; multilingual support requires retraining |
| **Class Imbalance** | Toxic comments are rare in real-world datasets; imbalanced training data can reduce precision |
| **Model Drift** | New slang, coded language, and evolving toxic patterns require periodic retraining |
| **False Positives** | Legitimate but edgy content may get flagged; human review is still recommended for high-stakes decisions |

---

## Future Enhancements

- [ ] Multi-label classification (toxic, severe toxic, obscene, threat, insult, identity hate)
- [ ] Fine-tuned transformer model (BERT / DistilBERT) for higher accuracy
- [ ] Support for multilingual comments
- [ ] Dashboard with real-time moderation analytics
- [ ] User feedback loop to continuously improve the model
- [ ] Docker containerization for easy deployment
- [ ] Integration guide for popular platforms (Discord, Reddit, etc.)

---

## Author

**Gokulavanan** — [gokulavanangk@gmail.com](mailto:gokulavanangk@gmail.com)

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

> *"Making online spaces safer, one prediction at a time."*
