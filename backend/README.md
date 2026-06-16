# AIRA — Artificial Intelligence Response Assistant for Student Wellness
## Core API Backend System Documentation

Welcome to the production-ready backend architectural core of **AIRA (Artificial Intelligence Response Assistant for Student Wellness)**. This directory contains the complete Python/Flask services, Hugging Face NLP transformers integrations, and MongoDB schemas that drive student diagnostics, mood heatmap temporal metrics, Gen-Z friendly conversational support agent nodes, and Haversine-based clinician spatial referrals.

---

## 🛠️ Technology Stack Specifications

- **Server Core:** Python 3.10+, Flask, Flask-Blueprint Core Modules
- **Cross-Origin Securities:** Flask-CORS (`r"/api/*"` restrictions)
- **Database Engine:** MongoDB (via standard PyMongo client drivers)
- **Cryptographic Portals:** PyJWT Bearer Authentication, Bcrypt Password Salting
- **Email Delivery:** Resend HTTP API (HTTPS port 443 — works on Render free tier)
- **Machine Learning Matrix:** SciKit-Learn Behavioral ML Model (Multilabel diagnostic predictions)
- **Natural Language Processing:** Hugging Face PyTorch Text Analysis Model Pipeline

---

## 📂 Backend Structural Layout

```text
backend/
├── app.py                      # Flask Application Root & DB Seeding Manager
├── config.py                   # Secure Configuration Variables (Env Decoders)
├── requirements.txt            # Python Module Dependencies List
├── .env                        # Local Environment Variable Decrypter (never committed)
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
│   ├── auth_routes.py          # OTP authentication, login, signup, profile
│   ├── prediction_routes.py    # ML assessment triggers & Text Analysis Model sentiments
│   ├── chatbot_routes.py       # Conversational chatbot loops & logs
│   ├── doctor_routes.py        # Haversine distance calculations sorted ascending
│   └── dashboard_routes.py     # Aggregated weekly timelines & heatmap blocks
└── services/                   # Business Logic Processing Units
    ├── email_service.py        # Unified email driver (Resend API primary, SMTP local fallback)
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
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
MONGO_URI=mongodb://localhost:27017/aira_wellness
PORT=5000
HOST=127.0.0.1

# Email delivery (Resend — required for production)
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxx
RESEND_FROM_ADDRESS=AIRA Wellness <noreply@yourdomain.com>

# Gmail SMTP (local dev fallback only — NOT used on Render)
SMTP_EMAIL=your-gmail@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 4. Start the Development Server
```bash
python app.py
```

*Note: In production environments, invoke the server using a WSGI server like Gunicorn:*
```bash
gunicorn -w 4 -b 0.0.0.0:10000 app:app
```

---

## 📧 Email Delivery Architecture

AIRA uses a **two-driver email system** managed by `services/email_service.py`:

| Environment | Driver | Port | Notes |
|---|---|---|---|
| **Production (Render)** | Resend HTTP API | 443 (HTTPS) | Set `RESEND_API_KEY` + `RESEND_FROM_ADDRESS` in Render env vars |
| **Local Development** | Gmail SMTP STARTTLS | 587 | Set `SMTP_EMAIL` + `SMTP_PASSWORD` in `.env` |

### Why not Gmail SMTP on Render?
Render free tier kernel-blocks all outbound TCP on ports 25, 465, and 587. Any direct SMTP connection fails with `[Errno 101] Network is unreachable`. Resend communicates over HTTPS port 443, which is never blocked.

### Resend Setup (Production)
1. Create a free account at [resend.com](https://resend.com) (3,000 emails/month free)
2. Verify your sending domain under **Domains**
3. Create an API key under **API Keys**
4. Add to Render environment: `RESEND_API_KEY` and `RESEND_FROM_ADDRESS`
5. Redeploy the Render service

---

## 🔒 Authentication & Security

### Login Paths
There is **exactly one** way to authenticate into AIRA:

| Path | Method | Description |
|---|---|---|
| Email + Password | `POST /api/login` | Standard login with Bcrypt-verified credentials |
| OTP Login | `POST /api/request-otp` → `POST /api/verify-otp` | Email-verified one-time password login |
| OTP Signup | `POST /api/signup-request-otp` → `POST /api/signup-verify-otp` → `POST /api/signup` | Email-verified registration |

> **No bypass paths exist.** OTP codes are never returned in API responses under any circumstance. Email delivery failure always returns HTTP 500 — the OTP is never exposed.

### JWT Bearer Token
Every endpoint under prediction, dashboard, doctor, or chatbot routes requires a validated JWT:
- **Header format:** `Authorization: Bearer <JWT_signature>`
- **Expiration:** 24 hours (configurable via `JWT_EXPIRATION_HOURS`)
- **Middleware:** `auth_middleware.py` validates tokens and injects `current_user` into handlers

### Password Security
- All passwords are Bcrypt-salted with a unique salt per user
- OTP codes are generated using `secrets.randbelow()` (cryptographically secure RNG)
- OTP codes are single-use — burned from the database immediately upon successful verification
- OTP codes expire after 5 minutes (enforced both by MongoDB TTL index and application-level check)

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

## 📡 REST API Blueprints Reference

### 🔐 Authentication Blueprints
- **`POST /api/signup`**: Registers name, email, and password — stores Bcrypt-salted credentials.
- **`POST /api/login`**: Verifies credentials, returns signed JWT token.
- **`POST /api/logout`**: Validates active session and signs student node off.
- **`GET /api/profile`**: Returns active student's name, identifiers, and sign-up dates.
- **`POST /api/request-otp`**: Generates 6-digit OTP and dispatches it to the user's email via Resend.
- **`POST /api/verify-otp`**: Verifies OTP, returns JWT token on success.
- **`POST /api/signup-request-otp`**: Checks email availability, dispatches signup OTP.
- **`POST /api/signup-verify-otp`**: Verifies signup OTP — confirms email ownership.
- **`POST /api/reset-password`**: Updates password after OTP verification.

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
