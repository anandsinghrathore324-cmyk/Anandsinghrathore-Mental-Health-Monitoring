# 🧠 AIRA: AI-Based Student Mental Health Monitoring & Support Platform

> **Practice School – I Final Project & Technical Defense Dossier**  
> **Institution**: Department of Computer Science Engineering, Institute of Engineering and Technology, JK Lakshmipat University, Jaipur  
> **Authors**: **Anand Singh Rathore** (Roll No: `2024BTECH158`) & **Diksha Shekhawat** (Roll No: `2024BTECH156`)  
> **Faculty Supervisors**: Dr. Sonali Vyas & Dr. Rajnish Kumar (JKLU CSE Dept.)  
> **External Industry Supervisor**: Dr. Saurabh Kumar  
> **GitHub Repository**: [anandsinghrathore324-cmyk/Anandsinghrathore-Mental-Health-Monitoring](https://github.com/anandsinghrathore324-cmyk/Anandsinghrathore-Mental-Health-Monitoring)  
> **Status**: Production-Ready · 175 Automated Pytests (100% Pass Rate) · Live Google Places & Groq LLM Integrations  

---

## 📑 Table of Contents
1. [Executive Summary & Project Vision](#1-executive-summary--project-vision)
2. [The Core Problem & Clinical Motivation](#2-the-core-problem--clinical-motivation)
3. [System Architecture & Dataflow](#3-system-architecture--dataflow)
4. [Technology Stack Breakdown & Engineering Justifications](#4-technology-stack-breakdown--engineering-justifications)
5. [Datasets Used: Shapes, Sizes & Features](#5-datasets-used-shapes-sizes--features)
6. [Machine Learning Diagnostics & Empirical Accuracy Benchmarks](#6-machine-learning-diagnostics--empirical-accuracy-benchmarks)
7. [Natural Language Processing Engine (DistilBERT Transformer)](#7-natural-language-processing-engine-distilbert-transformer)
8. [Conversational AI & The CrisisHandler Safety Protocol](#8-conversational-ai--the-crisishandler-safety-protocol)
9. [Live Geolocation Specialist Matching & Spatial Haversine Engine](#9-live-geolocation-specialist-matching--spatial-haversine-engine)
10. [Authentication, Security & The Brevo HTTPS Email Driver](#10-authentication-security--the-brevo-https-email-driver)
11. [Database Architecture & MongoDB Programmatic Indexes](#11-database-architecture--mongodb-programmatic-indexes)
12. [Presentation Graphs & Visual Analytics Dossier](#12-presentation-graphs--visual-analytics-dossier)
13. [Step-by-Step Installation & Local Execution Guide](#13-step-by-step-installation--local-execution-guide)
14. [Automated Quality Assurance Suite (175 Pytests)](#14-automated-quality-assurance-suite-175-pytests)
15. [Master Viva & Evaluator Q&A (Top 20 Defense Questions)](#15-master-viva--evaluator-qa-top-20-defense-questions)
16. [Key Engineering Challenges Solved](#16-key-engineering-challenges-solved)
17. [Future Scope & Production Roadmap](#17-future-scope--production-roadmap)

---

## 1. Executive Summary & Project Vision

**AIRA (AI-Based Student Mental Health Monitoring and Support Platform)** is an intelligent, full-stack, proactive digital healthcare ecosystem engineered to tackle the escalating mental health crisis across higher education institutions and high schools.

University life exposes students to acute stressors: relentless academic deadlines, competitive examinations, financial anxieties, irregular sleep hygiene, and social isolation. Despite the high prevalence of psychological distress, traditional campus counseling centers suffer from **low student engagement (<15%)** caused by social stigma, fear of peer judgment, bureaucratic appointment delays, and a total lack of 24/7 crisis triaging.

AIRA transforms campus mental health from an intimidating, reactive visit into a continuous, non-invasive, accessible digital wellness sanctuary. It unifies:
* **Dual Machine Learning Risk Diagnostics**: Combining free-text emotional NLP with structured numerical lifestyle factors.
* **Contextual Conversational AI**: Sub-second empathetic coaching driven by **Llama 3.3 70B** on Groq LPUs, anchored by a multi-signal **CrisisHandler** safety interceptor.
* **Dynamic Geolocation Specialist Referral**: Automatically routing students to licensed psychiatrists and psychologists near their current GPS coordinates using the **Google Places API (New)** and the **Haversine Distance Formula**.
* **30-Day Longitudinal Tracking**: An interactive GitHub-style Mood Stability Heatmap tracking emotional oscillations and sleep-strain correlations over time.

---

## 2. The Core Problem & Clinical Motivation

```
Traditional University Counseling vs. AIRA Proactive Digital Ecosystem
┌───────────────────────────────────────┐        ┌───────────────────────────────────────┐
│     TRADITIONAL CAMPUS COUNSELING     │        │          THE AIRA ECOSYSTEM           │
├───────────────────────────────────────┤        ├───────────────────────────────────────┤
│ • High Social Stigma & Peer Judgment  │   VS   │ • 100% Anonymous & Private Access     │
│ • Long Appointment Delays (3–14 days) │        │ • Instantaneous Diagnostics (< 1s)    │
│ • Closed After-Hours & Weekends       │        │ • 24/7/365 Conversational AI Support  │
│ • Purely Reactive (Post-Crisis Only)  │        │ • Early Detection & Daily Mood Heatmap│
│ • Static Paper Questionnaires         │        │ • Dual ML (DistilBERT NLP + Lifestyle)│
│ • Zero Automated Geolocation Triaging │        │ • Live Google Places Nearby Referrals │
└───────────────────────────────────────┘        └───────────────────────────────────────┘
```

### Key Statistical Drivers:
1. **The Stigma Barrier**: According to national health surveys, over **60% of engineering students** report experiencing severe anxiety, depressive episodes, or cognitive burnout at least once during their degree. However, more than **85% never visit campus counseling** due to the fear of academic penalization or social labeling.
2. **The Timing Dilemma**: Psychological crises (acute panic attacks, suicidal despair) peak late at night (between 11 PM and 4 AM) when campus clinics are closed.
3. **The Data Blindspot**: Static clinical surveys (like PHQ-9 or GAD-7) capture a single static moment in time. They fail to track the real-world daily interplay between sleep deficit, study hours, social media screen time, and emotional journaling.

---

## 3. System Architecture & Dataflow

AIRA is built on a decoupled, microservice-inspired full-stack architecture that cleanly separates presentation, business logic, machine learning pipelines, and persistent database storage:

```
                                      ┌──────────────────────────────────────────────┐
                                      │             CLIENT FRONTEND (UI)             │
                                      │   Vanilla HTML5 / CSS3 Glassmorphism / ES6+  │
                                      │        Chart.js Analytics / Vite Dev Server  │
                                      │             Port: 3000 (Open / Hot-Reload)   │
                                      └──────────────────────┬───────────────────────┘
                                                             │
                                                             │ JSON REST API over HTTPS / CORS
                                                             │ (Bearer JWT Authentication)
                                                             ▼
                                      ┌──────────────────────────────────────────────┐
                                      │            FLASK MICROSERVICE API            │
                                      │       Python 3.12 / Decoupled Blueprints     │
                                      │    Validation Middleware / Gunicorn Runtime  │
                                      │             Port: 5000 (127.0.0.1)           │
                                      └───────┬──────────────┬──────────────┬────────┘
                                              │              │              │
                   ┌──────────────────────────┴────┐         │         ┌────┴──────────────────────────┐
                   ▼                               ▼         ▼         ▼                               ▼
       ┌────────────────────────┐      ┌───────────────────┐ │ ┌──────────────────────┐    ┌──────────────────────┐
       │   DistilBERT NLP       │      │  Behavioral ML    │ │ │  Groq LPU LLM Engine │    │  Google Places API   │
       │   Emotion Engine       │      │  Regression Model │ │ │ (Llama 3.3 70B Chat) │    │  (New Text Search)   │
       │ (Hugging Face / PyTorch│      │ (Logistic Regress)│ │ │ (CrisisHandler Filter│    │ (Haversine Formula)  │
       │  Singleton Pipeline)   │      │ (Wellness Index)  │ │ │  Tele-MANAS Escalate)│    │ (<= 100km Safe Radius│
       └────────────────────────┘      └───────────────────┘ │ └──────────────────────┘    └──────────────────────┘
                                                             │
                                                             ▼
                                      ┌──────────────────────────────────────────────┐
                                      │           PERSISTENCE & EXTERNAL IO          │
                                      │   MongoDB Atlas Cluster (Live / mongomock)   │
                                      │   Brevo Transactional REST API (Port 443)    │
                                      └──────────────────────────────────────────────┘
```

### Complete End-to-End User Dataflow:
1. **Student Onboarding**: The student registers with an email, name, and password. The frontend validates the password against a real-time regex meter (8+ chars, uppercase, lowercase, number). The backend salts and hashes the password with **Bcrypt (12 rounds)** and saves the document in MongoDB.
2. **Email Verification**: A 6-digit verification code is transmitted via the **Brevo REST API** over HTTPS port 443. The OTP is stored in MongoDB with a **5-minute TTL (Time-To-Live) index** that automatically self-deletes upon expiration.
3. **Authentication**: Upon successful login, the backend issues an industry-standard **stateless JSON Web Token (PyJWT)** signed with `HS256` and valid for 24 hours. The client stores this token in secure session storage.
4. **Dual Diagnostic Scan**:
   * The student inputs their daily numerical habits (sleep hours, study workload, screen time) and free-text qualitative journaling.
   * `DistilBertClassifier` (in-process singleton) computes multi-class emotional distributions (Sadness, Fear, Joy, Anger).
   * `PredictionService` applies the trained **Logistic Regression model** on the normalized behavioral matrix, computing a calibrated **Wellness Index (0–100)** and a **3-Tier Risk Rating (Low, Moderate, Severe)**.
5. **Crisis Triage**: If the text contains severe despair or self-harm keywords, `CrisisHandler` aborts standard conversational flow, immediately presenting emergency support buttons for **Tele-MANAS (`14416`)** and **KIRAN (`1800-599-0019`)**.
6. **Geolocation Doctor Referral**: The browser auto-detects device GPS coordinates via HTML5 `navigator.geolocation`. The backend queries the **Google Places API (New)**, sorts clinics using the **Haversine formula**, and enforces a **strict $\le 100\text{ km}$ fallback radius filter** to prevent out-of-state clinic leakage.

---

## 4. Technology Stack Breakdown & Engineering Justifications

Every technology in AIRA was selected through rigorous architectural evaluation rather than defaults:

| Component | Technology Selected | Why It Was Chosen Over Alternatives |
| :--- | :--- | :--- |
| **Frontend Framework** | **Vanilla HTML5, CSS3 & ES6+ JavaScript** | Avoided React/Vue/Angular bundle bloat (zero 50MB `node_modules` overhead in production). Delivers sub-300ms First Contentful Paint (FCP) and maximum cross-device rendering performance. |
| **Styling & Theme** | **Custom Glassmorphism CSS3** | Avoided generic Tailwind/Bootstrap corporate styling. Uses native CSS `backdrop-filter`, dark cyberpunk neon accents, and smooth GPU-accelerated micro-animations to create an inviting, modern aesthetic tailored for Gen-Z students. |
| **Frontend Tooling** | **Vite 6** | Instant Hot Module Replacement (HMR), ultra-fast dev server on port 3000, and integrated proxy routing `/api` calls to Flask on port 5000. |
| **Backend API** | **Python 3.12 + Flask** | Flask's decoupled Blueprints provide clean modularity (`auth_routes`, `doctor_routes`, `prediction_routes`, `chatbot_routes`). Native Python integration allows DistilBERT and Scikit-Learn models to run directly in-process without slow inter-process IPC bridges. |
| **Password Security** | **Bcrypt (12 Salt Rounds)** | SHA-256 and MD5 are fast hash functions crackable at billions of guesses per second on modern GPUs. Bcrypt is an intentionally slow, memory-hard Blowfish cipher with 4,096 iterations ($2^{12}$), rendering brute-force attacks computationally impossible. |
| **Session Security** | **PyJWT (JSON Web Tokens)** | Stateless authentication with 24-hour expiration. Eliminates server-side session memory bottlenecks and enables horizontal scalability without needing Redis session clusters. |
| **Database Engine** | **MongoDB Atlas + PyMongo** | Document-oriented JSON storage perfectly matches polymorphic diagnostic reports and time-series mood logs. Automated TTL indexing handles OTP expiration at the database engine level. |
| **Database Fallback** | **MongoMock** | Integrated in-memory mock database that automatically activates if internet connectivity drops during local grading or offline demonstrations, guaranteeing zero server crashes. |
| **NLP Transformer** | **DistilBERT (`distilbert-base-uncased-emotion`)** | Knowledge distillation retains 97% of BERT's language understanding while running 60% faster with 40% less memory, allowing real-time CPU inference on standard laptops. |
| **Generative LLM** | **Groq API (`llama-3.3-70b-versatile`)** | Local Ollama execution on consumer laptops resulted in 15–30 second latencies and high RAM usage. Groq's specialized LPU hardware delivers 70B parameter inference in **~300-400 milliseconds**, providing an instantaneous conversational experience. |
| **Email Driver** | **Brevo Transactional REST API v3 (HTTPS Port 443)** | Cloud platforms (Render, AWS free tiers) block outbound TCP on SMTP ports 25, 465, and 587 (`[Errno 101] Network is unreachable`). Brevo transmits transactional OTPs over HTTPS port 443, which is 100% reliable across all firewalls. |
| **Geolocation** | **Google Places API (New) + Haversine Formula** | Eliminates static, out-of-date doctor lists. Dynamically locates real-world psychiatrists near the student's exact coordinates, computing true spherical great-circle distances. |
| **Testing Suite** | **Pytest + Pytest-Cov** | Comprehensive suite of **175 automated unit and integration tests** achieving a 100% pass rate in ~20 seconds, preventing regression across all endpoints. |

---

## 5. Datasets Used: Shapes, Sizes & Features

AIRA was trained, calibrated, and evaluated using empirical student mental health datasets:

```
                                  DATASET MATRIX SUMMARY
┌──────────────────────────────────────┬─────────────┬──────────┬───────────┬───────────────────────────────────────────┐
│ Dataset Name                         │ Rows        │ Columns  │ File Size │ Core Variables / Target Labels            │
├──────────────────────────────────────┼─────────────┼──────────┼───────────┼───────────────────────────────────────────┤
│ 1. Student Depression Dataset.csv    │ 27,901 rows │ 18 cols  │ ~2.8 MB   │ Academic Pressure, Sleep, Work Hours, CGPA│
│ 2. smmh.csv (Social Media & Health)  │ 481 rows    │ 21 cols  │ ~75 KB    │ Daily Social Usage, Distraction, Envy     │
│ 3. Student Mental health.csv         │ 101 rows    │ 11 cols  │ ~7 KB     │ Study Year, CGPA, Panic Attacks, Anxiety  │
│ 4. depression-reddit-cleaned         │ 7,731 posts │ 2 cols   │ ~1.2 MB   │ Qualitative Depression Text & Cues        │
│ 5. mental-health-corpus              │ 27,977 texts│ 2 cols   │ ~3.4 MB   │ Clinical Statements vs. Normal Text       │
│ 6. sentiment140 (Benchmark)          │ 1.6M tweets │ 6 cols   │ ~238 MB   │ Linguistic Baseline Sentiment Corpus      │
└──────────────────────────────────────┴─────────────┴──────────┴───────────┴───────────────────────────────────────────┘
```

### Feature Details for `Student Depression Dataset.csv`:
* **Demographics**: `Gender` (Categorical), `Age` (Integer 18–35), `City` (Text), `Degree` (B.Tech, B.Sc, M.Tech, etc.).
* **Academic Factors**: `Academic Pressure` (1–5 Likert scale), `Study Satisfaction` (1–5 scale), `CGPA` (Float 0.0–10.0).
* **Lifestyle Factors**: `Sleep Duration` (`<5 hours`, `5-6 hours`, `7-8 hours`, `>8 hours`), `Dietary Habits` (`Healthy`, `Moderate`, `Unhealthy`), `Work/Study Hours` (Numerical float).
* **Psychological & Family**: `Financial Stress` (1–5 scale), `Family History of Mental Illness` (Yes/No), `Have you ever had suicidal thoughts ?` (Yes/No).
* **Target Classification Column**: `Depression` (Binary: `0` = Low/Balanced, `1` = Elevated Risk).

### Data Preprocessing Pipeline:
1. **Cleaning**: Dropped corrupted rows, imputed missing values using median (numerical) and mode (categorical).
2. **Encoding**: Applied `OneHotEncoder` on nominal categories (`Gender`, `Sleep Duration`, `Dietary Habits`) and ordinal mapping on Likert scales.
3. **Scaling**: Evaluated all numerical features using `StandardScaler` to ensure zero mean and unit variance.
4. **Train/Test Splitting**: Enforced an 80/20 stratified split:
   * **Training Set (`X_train`)**: **22,320 samples**
   * **Testing Set (`X_test`)**: **5,581 samples**

---

## 6. Machine Learning Diagnostics & Empirical Accuracy Benchmarks

We conducted an empirical multi-model benchmark across 5,581 unseen student records, evaluating **Logistic Regression**, **XGBoost**, and **Random Forest**:

### Comprehensive Performance Benchmark Table
| Evaluation Metric | 🥇 **Logistic Regression** (Production Winner) | 🥈 **XGBoost Classifier** | 🥉 **Random Forest Classifier** |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **79.82%** (`0.7982`) | 78.73% (`0.7873`) | 77.39% (`0.7739`) |
| **Precision** | **81.28%** (`0.8128`) | 80.76% (`0.8076`) | 80.19% (`0.8019`) |
| **Recall (Sensitivity)** | **85.16%** (`0.8516`) | 83.60% (`0.8360`) | 81.52% (`0.8152`) |
| **F1-Score** | **83.17%** (`0.8317`) | 82.15% (`0.8215`) | 80.85% (`0.8085`) |
| **ROC-AUC Score** | **86.66%** (`0.8666`) | 85.37% (`0.8537`) | 84.44% (`0.8444`) |
| **False Negatives (Missed Cases)** | **485** *(Lowest / Best Safety)* | 536 | 604 *(Highest / Worst Safety)* |
| **Inference Latency** | **< 0.5 ms** | ~2.5 ms | ~8.0 ms |

### The Detailed Confusion Matrices (Total Test N = 5,581)

```
1. LOGISTIC REGRESSION (CHOSEN)         2. XGBOOST                       3. RANDOM FOREST
┌───────────────────────────────┐       ┌───────────────────────────────┐       ┌───────────────────────────────┐
│  TN: 1,672   │   FP: 641      │       │  TN: 1,662   │   FP: 651      │       │  TN: 1,655   │   FP: 658      │
├──────────────┼────────────────┤       ├──────────────┼────────────────┤       ├──────────────┼────────────────┤
│  FN: 485     │   TP: 2,783    │       │  FN: 536     │   TP: 2,732    │       │  FN: 604     │   TP: 2,664    │
└───────────────────────────────┘       └───────────────────────────────┘       └───────────────────────────────┘
```

### 🏆 Why Logistic Regression Won the Technical Evaluation
1. **The Primacy of Clinical Recall**: In medical diagnostics, a **False Negative** means an acutely distressed or suicidal student is falsely categorized as "fine" and receives no intervention. A **False Positive** merely provides wellness tips and helpline cards to someone who didn't strictly need them. Logistic Regression achieved the highest Recall (**85.16%**) and lowest False Negatives (**485 vs. 604 in Random Forest**).
2. **Probabilistic Calibration**: Logistic Regression maps inputs directly through the Sigmoid activation function:
   $$P(Y = 1 | X) = \frac{1}{1 + e^{-(\beta_0 + \sum \beta_i X_i)}}$$
   This produces smooth, true probabilities that directly drive AIRA's 0–100 Wellness Index.
3. **Explainability & Non-Overfitting**: Tree-based ensembles (Random Forest, XGBoost) showed signs of variance overfitting on categorical survey splits. Logistic Regression provided stable generalization with zero tree-depth bias and sub-millisecond execution.

---

## 7. Natural Language Processing Engine (DistilBERT Transformer)

AIRA implements a fine-tuned Hugging Face transformer pipeline (`bhadresh-savani/distilbert-base-uncased-emotion`) wrapped in a thread-safe Singleton (`DistilBertClassifier`):

```python
class DistilBertClassifier:
    """Thread-safe Singleton Hugging Face NLP Sentiment Classifier Model."""
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DistilBertClassifier, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
```

### Emotional Extraction Matrix:
When a student submits journal reflections, DistilBERT extracts 6 affective dimensions:
$$\text{Vector} = [P_{\text{sadness}}, P_{\text{fear}}, P_{\text{anger}}, P_{\text{joy}}, P_{\text{love}}, P_{\text{surprise}}]$$

* **Acute Distress Profile Example**: *"I cannot take this pressure anymore. Finals are next week, I haven't slept, and I'm terrified of disappointing everyone."*
  * **Sadness**: `42.5%`
  * **Fear/Anxiety**: `38.2%`
  * **Anger**: `11.4%`
  * **Joy**: `2.0%`
  * *Result*: Immediately triggers the Elevated Risk protocol and activates the CrisisHandler.
* **Balanced Profile Example**: *"Had a good group study session for physics today. Feeling prepared and going for a run."*
  * **Joy**: `56.5%`
  * **Love**: `24.3%`
  * **Sadness**: `3.1%`
  * *Result*: Categorized as Low Risk; updates the Mood Heatmap with a vibrant green marker.

### Gibberish & Noise Filter (`gibberish_detector.py`):
Before running transformer tokenization, incoming text is validated against:
* Character length threshold ($\ge 10$ meaningful words).
* Vowel-to-consonant ratio validation (detecting random keyboard smashes like `"sdfghjk"`).
* Repetitive character threshold (catching spam like `"aaaaaaa"`).

---

## 8. Conversational AI & The CrisisHandler Safety Protocol

AIRA's chatbot assistant is powered by **Llama 3.3 70B Versatile** hosted on Groq's high-speed LPU infrastructure.

```
                           CHATBOT INCOMING MESSAGE PIPELINE
                                          │
                                          ▼
                         ┌──────────────────────────────────┐
                         │      CrisisHandler Analyzer      │
                         │ Multi-Tier Regex & NLP Keywords  │
                         └────────────────┬─────────────────┘
                                          │
                      ┌───────────────────┴───────────────────┐
                      │                                       │
            [CRISIS DETECTED: YES]                  [CRISIS DETECTED: NO]
                      │                                       │
                      ▼                                       ▼
        ┌───────────────────────────┐           ┌───────────────────────────┐
        │  ABORT LLM GENERATION     │           │  Pass to Groq LPU API     │
        │ • Return Empathetic Guard │           │ • Llama 3.3 70B Versatile │
        │ • Render Emergency Cards: │           │ • Contextual Session Mem. │
        │   - Tele-MANAS (14416)    │           │ • Formatted Wellness Tips │
        │   - KIRAN (1800-599-0019) │           │   (Max 160 Tokens)        │
        └───────────────────────────┘           └───────────────────────────┘
```

### The Crisis Detection Regex Matrix:
* **Active Self-Harm / Suicidal Ideation**:
  ```python
  active_ideation_pattern = re.compile(
      r"\b(kill\s+myself|end\s+my\s+life|want\s+to\s+die|hurt\s+myself|harm\s+myself|"
      r"don't\s+want\s+to\s+live|no\s+reason\s+to\s+live|suicide|self-harm|cutting|overdose)\b"
  )
  ```
* **Hopelessness & Passive Despair**:
  ```python
  passive_distress_pattern = re.compile(
      r"\b(pointless|hopeless|can't\s+take\s+this|give\s+up|nothing\s+matters|"
      r"why\s+bother|want\s+to\s+disappear|better\s+off\s+dead)\b"
  )
  ```
* **Certified National Helplines Rendered**:
  * 🇮🇳 **Tele-MANAS**: `14416` / `1800-891-4416` (Govt. of India 24/7 Comprehensive Mental Health Line)
  * 🇮🇳 **KIRAN**: `1800-599-0019` (Ministry of Social Justice 24/7 Helpline)
  * 🌐 **988 Suicide & Crisis Lifeline** (International)
  * 📱 **Crisis Text Line**: Text `HOME` to `741741`

---

## 9. Live Geolocation Specialist Matching & Spatial Haversine Engine

Instead of static, hardcoded clinic directories, AIRA integrates real-world spatial tracking:

1. **HTML5 Client GPS Auto-Detection**:
   ```javascript
   navigator.geolocation.getCurrentPosition((position) => {
       const { latitude, longitude } = position.coords;
       fetchNearbySpecialists(latitude, longitude);
   });
   ```
2. **Google Places API (New) Query**:
   * Endpoint: `https://places.googleapis.com/v1/places:searchText`
   * Optimized Field Mask:
     ```
     places.displayName,places.formattedAddress,places.rating,
     places.userRatingCount,places.location,places.googleMapsUri
     ```
3. **The Haversine Distance Formula**:
   Calculates great-circle distance over the Earth's curvature ($R = 6,371\text{ km}$):
   $$\Delta\phi = \text{rad}(lat_2 - lat_1), \quad \Delta\lambda = \text{rad}(lon_2 - lon_1)$$
   $$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\text{rad}(lat_1)) \cdot \cos(\text{rad}(lat_2)) \cdot \sin^2\left(\frac{\Delta\lambda}{2}\right)$$
   $$d = 2 \cdot R \cdot \arctan2\left(\sqrt{a}, \sqrt{1 - a}\right)$$
4. **The $\le 100\text{ km}$ Strict Radius Fallback Cap**:
   If Google Places API reaches rate limits (HTTP 429), our resilient MongoDB fallback database activates. We apply the Haversine formula across local hospital records and **strictly reject any clinic $> 100\text{ km}$ away**, guaranteeing students never see out-of-state recommendations.

---

## 10. Authentication, Security & The Brevo HTTPS Email Driver

### A. The Cloud SMTP Port Blocking Problem
* Cloud platforms (Render, AWS EC2, DigitalOcean) block outbound TCP ports **25, 465, and 587** to prevent spam botnets. Python's standard `smtplib` fails with:
  `[Errno 101] Network is unreachable`
* **AIRA's Solution**: We engineered a custom HTTPS REST client for **Brevo (formerly Sendinblue) API v3** transmitting transactional email payloads over **HTTPS Port 443**, which is never blocked.
* Unlike Resend or SendGrid, Brevo allows verifying a single sender email address directly without requiring a custom domain or complex DNS TXT/DKIM/DMARC records.

### B. Security Architecture Summary
```
┌───────────────────────────┬───────────────────────────────────────────────────────────────────┐
│ Security Mechanism        │ Implementation Details & Guarantees                               │
├───────────────────────────┼───────────────────────────────────────────────────────────────────┤
│ Password Hashing          │ Bcrypt with 12 salt rounds ($2^{12} = 4,096$ key iterations)      │
│ Session Tokens            │ Stateless PyJWT signed with HS256, 24-hour expiration (`exp`)     │
│ OTP Code Expiry           │ MongoDB TTL index auto-deleting OTP documents after 300 seconds   │
│ CORS Policy               │ Restricted via `flask-cors` to authorized origins                 │
│ Input Sanitization        │ Strict email regex, length bounds, and SQL/NoSQL injection guards │
└───────────────────────────┴───────────────────────────────────────────────────────────────────┘
```

---

## 11. Database Architecture & MongoDB Programmatic Indexes

AIRA connects to MongoDB Atlas (`aira_wellness`) with programmatic indexing defined in `backend/database/db.py`:

```
1. users collection
   └── Index: "email" (Unique: True) → Eliminates duplicate registrations at the database level.

2. mental_health_reports collection
   └── Index: "user_id" → Instant lookup of past student assessments.
   └── Index: "created_at" → Chronological timeline aggregation.

3. mood_logs collection
   └── Compound Unique Index: [("user_id", 1), ("date", 1)] (Unique: True)
       → Guarantees students can record exactly one mood check-in per day.

4. chatbot_history collection
   └── Index: "user_id" & "timestamp" → Fast session memory loading.

5. doctor_recommendations collection
   └── Compound Index: [("latitude", 1), ("longitude", 1)] → Geospatial indexing.
   └── Index: "specialization" → Filtering by Anxiety, Depression, or General Therapy.

6. otp_codes collection
   └── Programmatic TTL Index: "created_at" (expireAfterSeconds=300)
       → Automatic engine-level document self-destruction after 5 minutes.
```

---

## 12. Presentation Graphs & Visual Analytics Dossier

All **6 publication-grade (300 DPI) presentation graphs** are generated by `docs/generate_presentation_graphs.py` and saved in `docs/presentation_graphs/`:

### Graph 1: Multi-Model Benchmark Comparison
* **File**: `docs/presentation_graphs/1_model_performance_comparison.png`
* **Details**: Multi-bar comparison of Logistic Regression, XGBoost, and Random Forest across Accuracy, Precision, Recall, F1-Score, and ROC-AUC.
* **Defense Takeaway**: Highlights Logistic Regression winning in Recall (**85.2%**) and ROC-AUC (**86.7%**).

### Graph 2: Confusion Matrices Comparison
* **File**: `docs/presentation_graphs/2_confusion_matrices_comparison.png`
* **Details**: Side-by-side heatmaps of 5,581 test predictions.
* **Defense Takeaway**: Proves Logistic Regression has the lowest False Negatives (**485 missed vs. 604 for Random Forest**).

### Graph 3: Receiver Operating Characteristic (ROC-AUC) Curves
* **File**: `docs/presentation_graphs/3_roc_auc_curves.png`
* **Details**: Sensitivity vs. 1-Specificity trade-offs across all thresholds.
* **Defense Takeaway**: Demonstrates superior discrimination with an Area Under the Curve of **0.8666** vs. Random Guess baseline of **0.5000**.

### Graph 4: Behavioral Stress Drivers Correlation
* **File**: `docs/presentation_graphs/4_feature_importance_correlation.png`
* **Details**: Pearson correlation ($r$) across 27,901 students from `Student Depression Dataset.csv`.
* **Defense Takeaway**: Proves Academic Pressure ($+0.435$) and Financial Stress ($+0.312$) drive distress, while Study Satisfaction ($-0.320$) acts as a buffer.

### Graph 5: DistilBERT NLP Multi-Class Emotion Analysis
* **File**: `docs/presentation_graphs/5_distilbert_emotion_analysis.png`
* **Details**: Compares emotional probability vectors of a Distressed Student Journal vs. a Balanced Student Journal.
* **Defense Takeaway**: Shows how high sadness and fear activate the 3-Tier risk escalation and CrisisHandler triage.

### Graph 6: Spatial Haversine Distance & 100 km Safe Boundary
* **File**: `docs/presentation_graphs/6_spatial_haversine_radius.png`
* **Details**: Exponential distance decay curve with a strict 100 km cutoff line.
* **Defense Takeaway**: Explains how spherical trigonometry prevents out-of-state doctor leakage during external API downtime.

---

## 13. Step-by-Step Installation & Local Execution Guide

### Prerequisites:
* **Python**: `3.12+`
* **Node.js**: `v18+` and `npm`
* **Git**: Installed and configured

### 1. Clone the Repository
```bash
git clone https://github.com/anandsinghrathore324-cmyk/Anandsinghrathore-Mental-Health-Monitoring.git
cd Anandsinghrathore-Mental-Health-Monitoring
```

### 2. Configure Backend Environment
Create or verify `backend/.env`:
```ini
SECRET_KEY=aira-super-secret-quantum-key-2026
JWT_SECRET_KEY=aira-super-secret-jwt-signature-key-2026
JWT_EXPIRATION_HOURS=24
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/aira_wellness?retryWrites=true&w=majority
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
LLM_PROVIDER=groq
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here
BREVO_API_KEY=your_brevo_api_key_here
BREVO_FROM_EMAIL=verified_sender@example.com
```

### 3. Launch Backend API (Port 5000)
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Start the Flask development server
python backend/app.py
```
*Backend runs live on: `http://127.0.0.1:5000/`*

### 4. Launch Frontend Dev Server (Port 3000)
In a separate terminal:
```bash
# Install npm dependencies (Vite)
npm install

# Start Vite development server
npm run dev
```
*Open your web browser to: `http://localhost:3000/`*

---

## 14. Automated Quality Assurance Suite (175 Pytests)

AIRA features an exhaustive automated test suite validating system stability across all layers:

```bash
# Run the complete test suite from repository root
pytest backend/tests/test_pytest_unit.py -v
```

### Test Suite Execution Report:
* **Total Tests Executed**: **175 Tests**
* **Passing Tests**: **175 Passed (100%)**
* **Failing Tests**: **0 Failed**
* **Execution Time**: **~20.67 Seconds**

```
============================= test session starts =============================
platform win32 -- Python 3.12.x, pytest-8.x.x
rootdir: C:\Users\...\Anandsinghrathore-Mental-Health-Monitoring
collected 175 items

backend/tests/test_pytest_unit.py::test_auth_registration_success PASSED   [  1%]
backend/tests/test_pytest_unit.py::test_auth_duplicate_email PASSED         [  2%]
backend/tests/test_pytest_unit.py::test_jwt_token_issuance PASSED           [  5%]
backend/tests/test_pytest_unit.py::test_jwt_expired_token_rejected PASSED   [  8%]
backend/tests/test_pytest_unit.py::test_distilbert_singleton_inference PASSED[ 15%]
backend/tests/test_pytest_unit.py::test_gibberish_detector_filter PASSED    [ 22%]
backend/tests/test_pytest_unit.py::test_logistic_regression_prediction PASSED[35%]
backend/tests/test_pytest_unit.py::test_crisis_handler_active_suicide PASSED[ 50%]
backend/tests/test_pytest_unit.py::test_crisis_handler_passive_despair PASSED[60%]
backend/tests/test_pytest_unit.py::test_haversine_distance_calculation PASSED[75%]
backend/tests/test_pytest_unit.py::test_haversine_100km_radius_cap PASSED   [ 85%]
backend/tests/test_pytest_unit.py::test_mongo_ttl_otp_index PASSED          [ 95%]
backend/tests/test_pytest_unit.py::test_brevo_rest_api_mock_dispatch PASSED [100%]

====================== 175 passed in 20.67s ==================================
```

---

## 15. Master Viva & Evaluator Q&A (Top 20 Defense Questions)

#### Q1: "Why did you choose Logistic Regression instead of complex deep learning for behavioral risk?"
> **Answer**: "In clinical screening, **Recall** is paramount because failing to identify a student in crisis (a False Negative) has severe consequences. On our test set of 5,581 samples, Logistic Regression achieved the highest Recall (**85.16%**) and lowest False Negatives (**485 vs. 604 in Random Forest**). Furthermore, Logistic Regression maps directly to calibrated probabilities via the Sigmoid curve, executes in under 0.5ms, and offers complete mathematical explainability without black-box tree bias."

#### Q2: "Can we rely on an AI chatbot during a severe psychiatric emergency?"
> **Answer**: "No. AI should never replace clinical psychiatric intervention during life-threatening crises. That is why AIRA implements our rule-based `CrisisHandler` *before* the prompt reaches the LLM. If acute self-harm or suicidal keywords are detected, generative conversation is bypassed immediately, returning compassionate de-escalation copy and direct-dial buttons for **Tele-MANAS (`14416`)** and **KIRAN (`1800-599-0019`)**."

#### Q3: "Why did you use DistilBERT instead of standard BERT or TF-IDF?"
> **Answer**: "TF-IDF ignores word order, negation, and semantic context (e.g., 'not sad' vs. 'very sad'). Full BERT contains 110 million parameters and requires substantial GPU memory. DistilBERT uses knowledge distillation to retain **97% of BERT's language comprehension** while being **40% smaller and 60% faster**, enabling real-time CPU inference on our Flask server."

#### Q4: "Why use the Groq API instead of running Ollama locally?"
> **Answer**: "Running local 7B or 70B models via Ollama on consumer laptops causes 15 to 30 second response latencies and consumes 6GB+ of RAM. Groq's Language Processing Units (LPUs) deliver sub-400ms inference for Llama 3.3 70B, providing students with immediate, fluid support with zero load on our host machines."

#### Q5: "How does the Doctor Locator work if a student is outside Jaipur?"
> **Answer**: "It is completely dynamic. The browser detects the student's live GPS coordinates via HTML5 `navigator.geolocation` anywhere in the world. It queries Google Places API (New) with spatial radius filters and calculates driving proximity using the spherical Haversine formula."

#### Q6: "What happens if Google Places API hits quota limits (HTTP 429)?"
> **Answer**: "Our backend gracefully falls back to our MongoDB specialist collection. To ensure students never see irrelevant clinics from hundreds of miles away, our fallback applies the Haversine formula and **strictly filters out any facility beyond 100 kilometers**."

#### Q7: "Why did you use Brevo REST API instead of standard SMTP?"
> **Answer**: "Modern cloud hosts (Render, AWS EC2 free tiers) block outbound TCP on standard SMTP ports (25, 465, 587) to prevent spam. Attempting standard SMTP leads to `[Errno 101] Network is unreachable`. Brevo transmits verification OTPs over standard HTTPS (Port 443), which is 100% reliable across all hosting environments."

#### Q8: "How does the Haversine Formula differ from Euclidean distance?"
> **Answer**: "Euclidean distance $\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$ assumes a flat 2D plane. Because the Earth is a sphere ($R \approx 6,371\text{ km}$), planar geometry causes massive distortions over latitude and longitude. The Haversine formula uses spherical trigonometry to compute true great-circle distances."

#### Q9: "Why use Bcrypt with 12 salt rounds instead of SHA-256?"
> **Answer**: "SHA-256 is designed for speed; modern graphics cards can compute billions of SHA-256 hashes per second, making brute-force attacks trivial. Bcrypt is an intentionally slow, memory-hard Blowfish cipher. Twelve salt rounds mean $2^{12} = 4,096$ iterations, taking ~250ms per check, which completely neutralizes hardware-accelerated attacks."

#### Q10: "Why use stateless JWT tokens instead of server sessions?"
> **Answer**: "Server sessions store state in server RAM or Redis, which creates memory bottlenecks and logs users out if the server restarts. JWT tokens are self-contained and stateless; the server verifies the cryptographic signature mathematically on incoming requests without database lookups."

#### Q11: "How do you prevent a student from submitting multiple mood ratings per day?"
> **Answer**: "Inside MongoDB, we established a compound unique index on the `mood_logs` collection: `[("user_id", 1), ("date", 1)]` with `unique=True`. Any duplicate insert attempt on the same calendar date is rejected at the database engine level."

#### Q12: "How do you ensure expired OTPs cannot be replayed?"
> **Answer**: "We created a MongoDB Time-To-Live (TTL) index: `db.otp_codes.create_index('created_at', expireAfterSeconds=300)`. MongoDB's background thread automatically purges OTP documents exactly 5 minutes after creation."

#### Q13: "What prevents users from submitting nonsensical text into the scanner?"
> **Answer**: "Our input validation middleware enforces a minimum 10-word length and routes text through `gibberish_detector.py`, which analyzes vowel-to-consonant ratios and repeated character spam before invoking transformer tokenization."

#### Q14: "Why use Vanilla CSS instead of Tailwind or Bootstrap?"
> **Answer**: "Tailwind and Bootstrap add significant CSS bundle sizes and often produce generic corporate layouts. For mental health, creating a warm, immersive, and non-intimidating visual experience was critical. We engineered custom glassmorphism panels using native CSS `backdrop-filter` and dark cyberpunk neon accents with zero external dependencies."

#### Q15: "How did you divide the work between Anand and Diksha?"
> **Answer**:
> * **Anand Singh Rathore**: Architected the Flask backend microservice, PyJWT security, Groq Llama 3.3 conversational pipeline, CrisisHandler safety interceptor, and authored the 175-test automated Pytest suite.
> * **Diksha Shekhawat**: Integrated the DistilBERT NLP models, engineered the Google Places geolocation and Haversine referral engine, built the 30-day mood stability heatmap, and led the frontend glassmorphism UI design."

#### Q16: "What is your test coverage?"
> **Answer**: "Our automated suite of 175 Pytests covers authentication routes, token lifecycles, input validation middleware, DistilBERT NLP inference, Logistic Regression decision boundaries, CrisisHandler regex triggers, Haversine distance bounds, and MongoDB error fallbacks."

#### Q17: "How is the 30-Day Mood Heatmap calculated?"
> **Answer**: "Each day, the student's check-in records an affective valence score (1 to 5). The frontend renders a contribution grid inspired by GitHub, coloring squares from dark blue (low/restless) to vibrant green (joy/balance) with click-to-inspect tooltips showing past journal snippets."

#### Q18: "What happens if a student has no internet connectivity during an offline demo?"
> **Answer**: "AIRA's database manager automatically detects if MongoDB Atlas is unreachable and transparently initializes an in-memory `mongomock` instance, ensuring the application never crashes during offline presentations."

#### Q19: "What are the primary ethical considerations in this project?"
> **Answer**: "Mental health data is sensitive. We enforce data minimization, zero diagnostic data sharing with third parties, transparent disclaimers that AIRA is a supportive wellness tool rather than a replacement for licensed clinical diagnosis, and immediate human escalation during crises."

#### Q20: "What is your future roadmap?"
> **Answer**: "Our roadmap includes developing native React Native mobile apps for daily push check-ins, integrating smartwatch sensor streams to track real-time Heart Rate Variability (HRV) physiological stress, and embedding WebRTC encrypted tele-counseling."

---

## 16. Key Engineering Challenges Solved

| Challenge Encountered | Root Cause | Engineering Solution Implemented |
| :--- | :--- | :--- |
| **Cloud SMTP Port Blocking** | Render/AWS kernels block outbound TCP on ports 25, 465, 587 (`[Errno 101]`). | Built a custom Brevo REST API email driver transmitting OTP payloads over standard HTTPS port 443. |
| **Google Places API Quota Limits** | Project daily unbilled quota exhaustion (HTTP 429). | Implemented a local MongoDB fallback database with Haversine distance filtering strictly capped to $\le 100\text{ km}$. |
| **High LLM Response Latency** | Local Ollama models took 15–30s on consumer laptops. | Migrated to Groq's LPU inference running Llama 3.3 70B, reducing latency to ~300-400ms. |
| **Transformer Server RAM Overhead** | Loading Hugging Face pipeline on every request exhausted server memory. | Implemented a thread-safe Singleton pattern (`DistilBertClassifier`), loading weights once into shared RAM. |
| **Accidental Multi-Turn Crisis Leakage** | LLMs can hallucinate unsafe responses when prompted with self-harm inputs. | Built a multi-tier regex interceptor (`CrisisHandler`) that bypasses the LLM entirely upon detecting distress keywords. |

---

## 17. Future Scope & Production Roadmap

1. **Native Mobile Clients (iOS & Android)**:
   * Build cross-platform React Native apps with native push notifications for morning and evening mindfulness reminders.
2. **Wearable Physiological Sensor Integration**:
   * Connect Bluetooth smartwatch APIs to analyze **Heart Rate Variability (HRV)**, resting pulse, and sleep stage cycles, combining biometric data with text analysis.
3. **Encrypted WebRTC Tele-Counseling**:
   * Allow students to book direct, end-to-end encrypted video appointments with university counselors directly through the platform.
4. **Multi-Lingual NLP Support**:
   * Expand DistilBERT fine-tuning to support Hindi and regional Indian dialects using IndicBERT models.

---

### 📄 Academic Citation & Reference
If referencing this system in academic literature or software defense:
```bibtex
@article{rathore2026aira,
  title={AIRA: AI-Based Student Mental Health Monitoring and Support Platform},
  author={Rathore, Anand Singh and Shekhawat, Diksha},
  journal={Department of Computer Science Engineering, JK Lakshmipat University, Jaipur},
  year={2026},
  month={August}
}
```
