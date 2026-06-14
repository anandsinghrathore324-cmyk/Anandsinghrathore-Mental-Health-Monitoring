# AIRA — Artificial Intelligence Response Assistant for Student Wellness
## Core API Backend System Documentation

Welcome to the production-ready backend architectural core of **AIRA (Artificial Intelligence Response Assistant for Student Wellness)**. This directory contains the complete Python/Flask services, Hugging Face NLP transformers integrations, and MongoDB schemas that drive student diagnostics, mood heatmap temporal metrics, Gen-Z friendly conversational support agent nodes, and Haversine-based clinician spatial referrals.

---

## 🛠️ Technology Stack Specifications

- **Server Core:** Python 3.10+, Flask, Flask-Blueprint Core Modules
- **Cross-Origin Securities:** Flask-CORS (`r"/api/*"` restrictions)
- **Database Engine:** MongoDB (via standard PyMongo client drivers)
- **Cryptographic Portals:** PyJWT Bearer Authentication, Bcrypt Password Salting
- **Machine Learning Matrix:** SciKit-Learn Behavioral ML Model (Multilabel diagnostic predictions)
- **Natural Language Processing:** Hugging Face PyTorch Text Analysis Model Pipeline

---

## 📂 Backend Structural Layout

```text
backend/
├── app.py                      # Flask Application Root & DB Seeding Manager
├── config.py                   # Secure Configuration Variables (Env Decoders)
├── requirements.txt            # Python Module Dependencies List
├── .env                        # Local Environment Variable Decrypter
├── database/                   # MongoDB Collection Model Frameworks
│   ├── db.py                   # DB Manager, Index Deployer & Unique Constraints
│   ├── user_model.py           # Bcrypt verification & standard search indexes
│   ├── report_model.py         # Assessment diagnostic report records
│   ├── mood_model.py           # Daily mood calendar entries
│   ├── chatbot_model.py        # Conversational dialogue retention matrices
│   └── doctor_model.py         # Psychological clinical geographical locations
├── middleware/                 # Flask Request Filters
│   └── auth_middleware.py      # Secure JWT validation interceptors
├── ml/                         # Advanced Machine Learning Pipelines
│   ├── preprocess.py           # Workload/sleep vectors transformer
│   ├── train_model.py          # Behavioral ML Model trainer script
│   └── saved_model.pkl         # Trained serialized machine learning weights
├── nlp/                        # Cognitive Language Engines
│   └── distilbert.py           # Text Analysis Model Singleton with rule fallbacks
├── routes/                     # Blueprint API Endpoint Handlers
│   ├── auth_routes.py          # Signup, login verification, student profiles
│   ├── prediction_routes.py    # ML assessment triggers & Text Analysis Model sentiments
│   ├── chatbot_routes.py       # Conversational chatbot loops & logs
│   ├── doctor_routes.py        # Haversine distance calculations sorted ascending
│   └── dashboard_routes.py     # Aggregated weekly timelines & heatmap blocks
└── services/                   # Business Logic Processing Units
    ├── prediction_service.py   # Hybrid model/algorithmic diagnostic blenders
    ├── chatbot_service.py      # Context-rich support dialect generators
    ├── doctor_service.py       # Proximity location sorters
    ├── dashboard_service.py    # Chart.js list structures compilers
    └── nlp_service.py          # Text classifier gateways
```

---

## 🚀 Getting Started & Initialization

### 1. Prerequisite Installations
Ensure your terminal environment has a running instance of **MongoDB** (on port `27017` or via an Atlas connection string) and a **Python 3.10+** interpreter.

### 2. Virtual Environment Setup & Dependencies
Initialize a secure shell environment inside the `backend/` directory:

```bash
# Create standard environment
python -m venv venv

# Activate venv on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Install required modules
pip install -r requirements.txt
```

### 3. Environment Variables Settings
Review and configure `backend/.env` matching your MongoDB connection strings:

```ini
SECRET_KEY=aira-super-secret-quantum-key-2026
JWT_SECRET_KEY=aira-super-secret-jwt-signature-key-2026
MONGO_URI=mongodb://localhost:27017/aira_wellness
PORT=5000
HOST=127.0.0.1
```

### 4. Seed Verified Psychologists & Start Node
Run the application launcher. The server will dynamically verify database status, establish indexing rules on all collections, auto-generate default verified doctor registries across international regions, and launch the REST API nodes:

```bash
python app.py
```

*Note: In production environments, invoke the server using a WSGI server like Gunicorn:*
```bash
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

---

## 🧠 Core Machine Learning & NLP Pipelines

### A. The Hybrid Diagnostic Solver
The backend implements a two-layered diagnostic scoring routine:
1. **Behavioral ML Model pickle weights (`saved_model.pkl`):** Trained on workload variables, academic strain ratios, screen-time factors, and sleep deficit parameters to predict wellness indicators.
2. **Deterministic Clinical Formulas:** Modulates stress, anxiety, depression, and burnout based on high-pressure keyword vectors and daily sleep limits to ensure safety boundaries.
3. **Blending weight:** 80% deterministic clinical indicators, 20% ML regression variance mapping.

### B. Text Analysis Model Sentiment Analyzer
- Uses Hugging Face's `transformers` module to load a lightweight, highly accurate PyTorch Text Analysis Model.
- Analyzes student journal statements to extract positive, negative, and neutral weights.
- **Fail-safe Dictionary Fallback:** If the host processor is under memory constraints or offline, the singleton class catches exceptions and falls back to a lexical lookup loop with equal output formats to ensure 100% server uptime.

---

## 🔒 Security & Middleware Protocols
Every endpoint under prediction, dashboard compile, doctor sorting, or chatbot dialogue routes requires a validated session JWT Bearer token:
- **Header format:** `Authorization: Bearer <JWT_signature>`
- **Expirations:** 24 Hours default.
- **Middleware:** `auth_middleware.py` intercepts incoming payloads, validates token authenticity, searches user tables, and injects `current_user` object references directly into blueprint handlers.

---

## 📡 REST API Blueprints Reference

### 🔐 Authentication Blueprints
- **`POST /api/signup`**: Registers name, email, and returns Bcrypt salted records.
- **`POST /api/login`**: Verifies cryptographically, creates JWT signatures, returns token.
- **`POST /api/logout`**: Validates active session and signs student node off.
- **`GET /api/profile`**: Returns active student's name, identifiers, and sign-up dates.

### 📊 Diagnostic Predictions
- **`POST /api/predict`**: Blends behavioral variables and Text Analysis Model sentiment logs, logs reports, and updates the daily mood heatmap.
- **`POST /api/analyze-text`**: On-demand text analyzer returns sentiment weights.

### 💬 Supportive Chatbot Dialogues
- **`POST /api/chatbot`**: Retains conversational contexts, returns Gen-Z comforting dialogue, logs conversation maps.
- **`GET /api/chat-history`**: Compiles previous dialogue cards for instant client rendering.

### 📍 Spatial Referral Nodes
- **`POST /api/nearby-doctors`**: Takes spatial `latitude` and `longitude` coordinates, calculates real-time distances using spherical Haversine formulas, and returns psychologists sorted in ascending proximity order.

### 📈 Aggregated Dashboards
- **`GET /api/dashboard-data`**: Formulates Chart.js compatible timelines, gathers mood matrices, and calculates weekly stability indicators.
