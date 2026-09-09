# 🎓 AIRA — Comprehensive Presentation Master Guide & Defense Dossier
> **AI-Based Student Mental Health Monitoring & Support Platform**  
> **Course**: Practice School – I Final Examination & Defense  
> **Institution**: Department of Computer Science Engineering, JK Lakshmipat University, Jaipur  
> **Authors**: Anand Singh Rathore (2024BTECH158) & Diksha Shekhawat (2024BTECH156)  
> **Supervisors**: Dr. Sonali Vyas, Dr. Rajnish Kumar (Internal) & Dr. Saurabh Kumar (External)  

---

## 📌 Executive Summary (Elevator Pitch)
**AIRA** is a production-grade, full-stack proactive mental health monitoring ecosystem engineered specifically for higher education and high-school students. 

Traditional institutional counseling systems suffer from **high social stigma, long waiting queues, lack of real-time triaging, and zero proactive crisis interception**. AIRA solves this by combining:
1. **Dual Machine Learning Diagnostics**: Fine-tuned **DistilBERT NLP** (free-text emotional sentiment) + **Behavioral ML Regression** (academic load, sleep deficit, screen time).
2. **Contextual Conversational AI**: **Llama 3.3 70B Versatile** (via high-speed Groq API) featuring an active **CrisisHandler** multi-signal interceptor that detects suicidal ideation/acute distress in real-time.
3. **Live Geolocation Specialist Matching**: **Google Places API (New)** + HTML5 GPS auto-detection + mathematical **Haversine Distance Formula** (capping specialists strictly to $\le 100\text{ km}$).
4. **Empirical Software Quality**: A rigorous automated Pytest suite of **175 unit and integration tests with a 100% pass rate**.

---

## 🏛️ System Architecture & Technology Stack

```
                                    ┌───────────────────────────────────────────────┐
                                    │               STUDENT CLIENT                  │
                                    │    Vanilla HTML5 / CSS3 Glassmorphism / ES6+  │
                                    │         Chart.js Analytics / Vite Server      │
                                    └───────────────────────┬───────────────────────┘
                                                            │ HTTPS / REST (Port 3000 -> 5000)
                                                            ▼
                                    ┌───────────────────────────────────────────────┐
                                    │             FLASK MICROSERVICE API            │
                                    │    Python 3.12 / Blueprints / CORS / PyJWT    │
                                    └───────┬───────────────┬───────────────┬───────┘
                                            │               │               │
                     ┌──────────────────────┴────┐          │          ┌────┴──────────────────────┐
                     ▼                           ▼          ▼          ▼                           ▼
          ┌─────────────────────┐      ┌──────────────────┐ │ ┌──────────────────┐      ┌──────────────────┐
          │   DistilBERT NLP    │      │  Behavioral ML   │ │ │ Groq Llama 3.3   │      │  Google Places   │
          │   Sentiment Engine  │      │ Regression Model │ │ │   70B LLM Chat   │      │   API (New)      │
          │ (Joy/Sad/Anx/Anger) │      │ (Wellness Index) │ │ │ (CrisisHandler)  │      │ (Haversine Calc) │
          └─────────────────────┘      └──────────────────┘ │ └──────────────────┘      └──────────────────┘
                                                            │
                                                            ▼
                                    ┌───────────────────────────────────────────────┐
                                    │             DATABASE & EXTERNAL IO            │
                                    │  MongoDB Atlas (TTL Indexes, User, Reports)   │
                                    │  Brevo HTTPS REST API (Port 443 OTP Delivery) │
                                    └───────────────────────────────────────────────┘
```

### Full Tech Stack Breakdown
| Layer | Technologies Used | Justification / Engineering Rationale |
| :--- | :--- | :--- |
| **Frontend** | Vanilla HTML5, CSS3 Glassmorphic UI, Vanilla ES6+ JS, Chart.js, Vite | Zero framework overhead; ultra-fast initial paint (<300ms); custom dark cyberpunk aesthetics tailored for Gen-Z engagement. |
| **Backend API** | Python 3.12, Flask Framework, Flask-CORS, PyJWT, Bcrypt | Lightweight microservice design; native Python integration for ML model pipelines; secure stateless JWT token authentication. |
| **AI / NLP** | HuggingFace Transformers (DistilBERT), Scikit-Learn, Joblib | DistilBERT provides 97% of BERT's language understanding at 60% faster evaluation speeds and 40% less memory footprint. |
| **Generative LLM** | Groq API (`llama-3.3-70b-versatile`), Custom WellnessCoach loop | Sub-second inference latency (~250-400ms); multi-turn contextual memory; strict rule-based crisis pre-filtering. |
| **Spatial / Geo** | HTML5 Geolocation API, Google Places API (New), Haversine Algorithm | Real-time GPS auto-detection; live Google Maps verified clinics; spherical distance calculation eliminating static mock data. |
| **Database** | MongoDB Atlas Cloud Cluster (`aira_wellness`) | Flexible JSON document schema for multi-dimensional clinical reports; automatic TTL index for 5-minute OTP expirations. |
| **Email Service**| Brevo REST API v3 over HTTPS (Port 443) | Bypasses ISP and cloud provider (Render/AWS) SMTP port blocking (ports 25, 465, 587) with guaranteed email delivery. |
| **Quality Assurance**| Pytest, Pytest-Cov, Unittest Mocks | 175 automated unit and integration tests guaranteeing 0% breaking changes across routes, auth, ML, and database layers. |

---

## 🧠 The 3 Core AI & Intelligence Engines

### 1. NLP Sentiment Diagnostic Engine (DistilBERT)
- **Input**: Free-text qualitative journaling ("I feel overwhelmed by upcoming exams and haven't slept in 3 days").
- **Processing**: Tokenized and evaluated via a fine-tuned DistilBERT transformer.
- **Output**: Multi-class probability distribution:
  $$\text{Sentiment Matrix} = \{\text{Joy}: P_j, \text{Sadness}: P_s, \text{Anxiety}: P_a, \text{Anger}: P_{ang}\}$$
- **Gibberish / Noise Filtering**: Dedicated regex and heuristic linguistic validator rejects keystroke spam or nonsensical inputs before ML evaluation.

### 2. Behavioral Lifestyle Regression Engine
- **Input**: Quantitative student habits:
  - Daily sleep hours (vs. recommended 8h)
  - Study hours & academic workload rating (1-10)
  - Screen time & social media consumption (hours)
  - Self-reported psychological distress score (1-10)
- **Output**: Calibrated **Wellness Index (0 to 100)** and a **3-Tier Risk Rating**:
  - 🟢 **Low Risk (Score $\ge 70$)**: Positive coping strategies, balanced lifestyle habits.
  - 🟡 **Moderate Risk (Score $45 - 69$)**: Cognitive strain, sleep hygiene tips, guided journaling.
  - 🔴 **High / Severe Risk (Score $< 45$)**: Immediate priority specialist matching + 24/7 hotline intercept.

### 3. AIRA Conversational Orchestrator & Crisis Protocol
- **Model**: `llama-3.3-70b-versatile` running via Groq low-latency inference.
- **Safety-First Crisis Interception (`CrisisHandler`)**:
  - Pre-evaluates incoming user messages before sending them to the LLM.
  - Detects active self-harm, suicidal ideation, or acute distress via multi-tier regex and NLP keywords.
  - If a crisis is detected, normal conversational flow is **immediately bypassed**, returning an empathetic, de-escalating safety response and prominent emergency hotline cards:
    - **Tele-MANAS**: 14416 / 1800-891-4416 (24/7 Govt of India Helpline)
    - **KIRAN**: 1800-599-0019 (Mental Health Rehabilitation)
    - **988 Lifeline & Crisis Text Line** (International / Global)
- **Contextual Session Memory (`MemoryManager`)**: Stores active conversation history per authenticated user ID so follow-up interactions maintain full clinical context.

---

## 📍 Live Specialist Geolocation & Spatial Haversine Engine

1. **HTML5 Device Geolocation**: On opening the specialist referral page, the browser queries `navigator.geolocation.getCurrentPosition()`.
2. **Google Places API (New) Text Search**:
   Queries `https://places.googleapis.com/v1/places:searchText` using field mask optimization (`places.displayName`, `places.formattedAddress`, `places.rating`, `places.userRatingCount`, `places.location`, `places.googleMapsUri`).
3. **The Haversine Distance Formula**:
   Calculates great-circle distance between user $(lat_1, lon_1)$ and clinic $(lat_2, lon_2)$:
   $$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$
   $$d = 2R \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1-a}\right) \quad (\text{where } R = 6371\text{ km})$$
4. **Resilient Fallback Policy**:
   If Google Places API reaches rate limits (HTTP 429), AIRA falls back to a curated database of verified psychiatric facilities (e.g., SMS Hospital Psychiatric Centre, Fortis Mental Health Jaipur), **strictly filtered to $\le 100\text{ km}$** using Haversine calculation to prevent distant clinics from leaking.

---

## 🎯 12-Slide Presentation Walkthrough & Speech Script

### Slide 1: Title & Introduction
* **Visual**: Project Logo, Student Details (Anand & Diksha), Supervisors, JKLU Crest.
* **Speaker Script**:
  > "Respected supervisors, examiners, and faculty members. Good morning. Today, we are proud to present **AIRA: An AI-Based Student Mental Health Monitoring and Support Platform**. Higher education brings immense opportunity, but it also carries unprecedented academic anxiety, sleep deprivation, and burnout. AIRA was engineered to bridge the gap between struggling students and timely, stigma-free psychological care."

### Slide 2: The Problem Statement & Industry Reality
* **Visual**: Statistics on student mental health, barriers to care (stigma, delays, lack of 24/7 support).
* **Speaker Script**:
  > "Over 60% of university students report severe academic stress or depressive symptoms at least once during their academic journey. However, less than 15% seek institutional counseling. Why? Three barriers: Fear of judgment, appointment delays of days or weeks, and the absence of immediate crisis triage during midnight hours. AIRA transforms mental health monitoring from a reactive visit to an accessible, proactive digital ecosystem."

### Slide 3: The AIRA Solution Overview
* **Visual**: UI screenshots showing the Scanner, the Chatbot, the Mood Heatmap, and Doctor Recommendations.
* **Speaker Script**:
  > "AIRA provides an all-in-one platform offering three interconnected pillars: First, **Dual ML Risk Diagnostics** that evaluate both what a student writes and how they live. Second, an **Empathetic AI Companion** powered by Llama 3.3 70B with an automated crisis safety net. Third, a **Spatial Geolocation Specialist Locator** that automatically finds real-world psychologists within driving distance."

### Slide 4: System Architecture
* **Visual**: Full architectural block diagram (Client $\leftrightarrow$ Flask API $\leftrightarrow$ ML / Groq / Google Places $\leftrightarrow$ MongoDB).
* **Speaker Script**:
  > "Architecturally, AIRA is a decoupled full-stack platform. The frontend is built on Vanilla HTML5, glassmorphic CSS, and modern JavaScript, served via Vite with zero framework bloat. The backend is a modular Flask microservice in Python 3.12, orchestrating JWT authentication, MongoDB Atlas persistence, and external REST APIs like Google Places and Groq."

### Slide 5: Dual Machine Learning Diagnostics
* **Visual**: Graphs of DistilBERT sentiment extraction and Behavioral Wellness Index calculation.
* **Speaker Script**:
  > "Instead of relying solely on arbitrary questionnaires, our diagnostic engine uses two distinct models:
  > 1. Our **NLP Model** uses a fine-tuned DistilBERT transformer to analyze the student's free-text journaling, extracting emotional probabilities across joy, sadness, anxiety, and anger.
  > 2. Our **Behavioral ML Model** analyzes quantitative markers like sleep deficit, study-to-break ratios, and screen time to compute an overarching Wellness Index from 0 to 100, categorizing the student into Low, Moderate, or Severe risk."

### Slide 6: The Conversational AI & Crisis Protocol
* **Visual**: Chat interface showing normal coaching conversation vs. immediate CrisisHandler interception card.
* **Speaker Script**:
  > "Our chatbot runs on Groq's ultra-fast Llama 3.3 70B engine. However, when dealing with mental health, AI safety is paramount. We implemented an independent **CrisisHandler** that scans every message before the LLM processes it. If explicit or implicit suicidal ideation or self-harm is detected, the AI conversation is superseded by immediate, warm de-escalation protocols and clickable 24/7 hotlines like Tele-MANAS and KIRAN."

### Slide 7: Live Geolocation Doctor Recommendation Engine
* **Visual**: Google Places integration, interactive map cards, distance badges (e.g., '3.2 km away'), clinic ratings.
* **Speaker Script**:
  > "Most student health apps show hardcoded doctor lists. AIRA is dynamic: upon user permission, it captures live device GPS coordinates, queries Google Places API (New), and applies the **Haversine Distance Formula** to rank nearby licensed psychologists and clinics by proximity. If external APIs hit quota limits, our resilient fallback engine activates, strictly filtering regional specialists to within 100 kilometers."

### Slide 8: Student Dashboard & 30-Day Mood Analytics
* **Visual**: Interactive 30-day GitHub-style mood stability heatmap, Chart.js sentiment pie charts.
* **Speaker Script**:
  > "In the student dashboard, users gain longitudinal self-awareness. AIRA features a 30-day interactive Mood Stability Heatmap inspired by contribution graphs. Students can click any previous day to inspect past sentiment patterns, journal entries, sleep correlations, and behavioral trends over time."

### Slide 9: Security, Privacy & Authentication
* **Visual**: Bcrypt password hashing, PyJWT tokens, real-time password strength meter, Brevo HTTPS OTP dispatch.
* **Speaker Script**:
  > "Mental health data demands strict confidentiality. We implemented stateless JWT tokens with 24-hour expiration, Bcrypt password hashing, and input validation schemas. For password recovery and account activation, we built a custom Brevo REST API email driver that transmits 6-digit OTPs over HTTPS port 443, eliminating SMTP port-blocking vulnerabilities."

### Slide 10: Engineering Challenges Solved
* **Visual**: Before-and-after table: Milestone prototype vs. Final production state; HTTP 429 quota handling diagram.
* **Speaker Script**:
  > "Between milestone review and this final submission, we overcame two major engineering bottlenecks:
  > 1. Cloud SMTP port blocking on Render: solved by migrating from standard SMTP to HTTPS REST email delivery.
  > 2. Google Places API quota throttling: solved by creating a robust local fallback database with live Haversine spatial filtering, ensuring zero blank screens even under network failure."

### Slide 11: Empirical Quality Assurance (175 Tests)
* **Visual**: Pytest terminal screenshot showing `175 passed in 20.67s`, 100% pass rate.
* **Speaker Script**:
  > "To verify production readiness, we engineered a comprehensive test suite of **175 automated unit and integration tests** using Pytest. Every route, token validation, ML pipeline, Haversine calculation, and crisis regex pattern was tested against positive, negative, and edge cases, achieving a 100% pass rate."

### Slide 12: Future Roadmap & Conclusion
* **Visual**: Mobile mockup (React Native), Smartwatch wearable sensor (HRV), WebRTC video counseling.
* **Speaker Script**:
  > "Looking ahead, our roadmap includes a React Native mobile client, smartwatch integration for real-time Heart Rate Variability (HRV) stress tracking, and WebRTC tele-counseling. AIRA proves that AI can be both mathematically rigorous and deeply empathetic in safeguarding student well-being. Thank you, and we now welcome your questions."

---

## 💻 Live Demo Step-by-Step Execution Plan

When presenting your screen, follow this exact sequence:

1. **Step 1: Launch the System**
   - Show terminal: Frontend running on `http://localhost:3000/` (Vite) and Flask running on `http://127.0.0.1:5000/`.
   - Open browser to `http://localhost:3000/`.
2. **Step 2: Sign-Up / Validation**
   - Click **Get Started**. Show the real-time password validation meter (8+ characters, uppercase, lowercase, number).
   - Log in with existing account or demo account.
3. **Step 3: Run the Mental Health Scanner**
   - Navigate to the **Mental Health Scanner** section.
   - Enter journal text: *"I'm having constant anxiety about my engineering finals, haven't slept more than 4 hours, and feel burnt out."*
   - Set sliders: Sleep: 4 hrs, Study: 9 hrs, Screen Time: 7 hrs.
   - Click **Run Neural Scan**.
   - **Highlight**: Watch the dual ML output render in under 1 second — DistilBERT emotional percentage (high Anxiety + Sadness), behavioral Wellness Index score, and tailored coping advice.
4. **Step 4: Demonstrate the AI Chatbot & Crisis Safety Protocol**
   - Click the floating **AIRA Chatbot** icon.
   - Ask a normal wellness question: *"Can you suggest a 5-minute grounding exercise for exam stress?"*
   - Show the fast Llama 3.3 70B response formatted cleanly.
   - **The Killer Safety Demo**: Type: *"I feel completely hopeless and want to end it all."*
   - **Highlight**: Notice the immediate crisis takeover — conversation is safely intercepted, presenting warm support and prominent national emergency helpline buttons (Tele-MANAS, KIRAN).
5. **Step 5: Show Live Doctor Geolocation**
   - Click **Doctor Support** in the navbar.
   - Allow location access.
   - Show how the system queries nearby Jaipur/local psychologists with live ratings, addresses, distance badges, and clickable calling/maps links.
6. **Step 6: Show Automated Test Suite**
   - Open terminal and run:
     ```bash
     pytest backend/tests/test_pytest_unit.py -v
     ```
   - Show all 175 tests turning green!

---

## ❓ Top 15 Tough Examiner / Evaluator Questions & Winning Answers

#### Q1: "Why did you choose DistilBERT instead of regular BERT or standard TF-IDF?"
> **Answer**: "TF-IDF ignores semantic word context, negation, and linguistic order (e.g., 'not happy' vs. 'very happy'). Standard BERT, while powerful, has 110 million parameters and requires significant GPU memory, resulting in high API response latency. DistilBERT uses knowledge distillation to retain 97% of BERT’s language understanding while running 60% faster with 40% less memory, making in-process CPU inference fast and practical."

#### Q2: "What if a student experiences a severe crisis? Can we rely on an AI chatbot?"
> **Answer**: "No, AI should never replace clinical psychiatric care in life-threatening situations. That is why AIRA implements our rule-based `CrisisHandler` layer *before* any LLM inference occurs. If self-harm, suicidal ideation, or severe distress keywords are detected, the LLM is bypassed, and the user is immediately given direct-dial links to certified 24/7 national helplines like Tele-MANAS (14416) and KIRAN."

#### Q3: "How does your Doctor Recommendation system work if the student is in another city?"
> **Answer**: "The system uses the HTML5 Geolocation API to detect the student's exact device coordinates wherever they are in India or globally. It queries Google Places API (New) with spatial radius filters and computes exact real-world driving distance using the Haversine formula. It is completely dynamic and not restricted to Jaipur."

#### Q4: "What happens if Google Places API fails or runs out of credits?"
> **Answer**: "We engineered a graceful fallback architecture. If Google Places returns HTTP 429 (quota exhausted) or network error, `DoctorService` queries our MongoDB fallback collection. Crucially, we apply our Haversine spatial filter to those fallback records and cap the search radius to $\le 100\text{ km}$, ensuring students never see irrelevant clinics from another state."

#### Q5: "How are passwords and medical assessment reports secured?"
> **Answer**: "Passwords are salted and hashed using Bcrypt before ever touching the database. API authentication relies on stateless JSON Web Tokens (PyJWT) with a 24-hour expiration. MongoDB uses strict schema validation and indexed queries, ensuring students can only access their own reports."

#### Q6: "Why did you use Groq instead of running Ollama locally?"
> **Answer**: "In earlier milestones, running local Ollama models on consumer laptops caused 15 to 30 second response latencies and high RAM consumption, which degraded the student experience. By migrating to Groq's specialized LPU (Language Processing Unit) running Llama 3.3 70B, response latency dropped to under 400 milliseconds while delivering higher emotional intelligence and zero host machine load."

#### Q7: "Why did you use Brevo REST API instead of traditional SMTP?"
> **Answer**: "Major cloud platforms like Render, AWS, and DigitalOcean block outbound SMTP ports 25, 465, and 587 by default to prevent spam. Trying to send emails via standard SMTP led to connection timeouts. We built an HTTPS REST client for Brevo API v3, sending OTP requests over standard port 443, which is 100% reliable across all hosting environments."

#### Q8: "How does the Haversine Formula work in simple terms?"
> **Answer**: "Because the Earth is an oblate spheroid, simple Euclidean distance $(x_2 - x_1)^2 + (y_2 - y_1)^2$ causes massive inaccuracies over geographical distances. The Haversine formula accounts for the spherical curvature of the Earth using latitude and longitude radians, calculating the true great-circle distance."

#### Q9: "How did you test this system?"
> **Answer**: "We built an automated pytest suite containing 175 tests across unit and integration levels. It tests authentication endpoints, password validation schemas, ML input ranges, chatbot memory retention, crisis interception edge cases, Haversine distance calculations, and database failure recovery. All 175 tests pass in approximately 20 seconds."

#### Q10: "Can students fake their inputs in the journal text box?"
> **Answer**: "We built a multi-stage input validation middleware. It checks for minimum character lengths (at least 10 words), filters repetitive character spam (e.g., 'aaaaaa'), and passes text through a linguistic gibberish detector before invoking the transformer model."

#### Q11: "What is your database schema design in MongoDB?"
> **Answer**: "We have six decoupled collections:
> 1. `users`: profile, hashed password, institution details.
> 2. `mental_health_reports`: historical diagnostic scores, risk tier, sentiment breakdown.
> 3. `mood_logs`: daily mood check-in records powering the 30-Day Heatmap.
> 4. `chatbot_history`: dialogue turns indexed by `user_id` and timestamp.
> 5. `doctor_recommendations`: curated specialist database for offline fallbacks.
> 6. `otp_codes`: verification tokens equipped with a MongoDB TTL (Time-To-Live) index that automatically purges expired codes after 5 minutes."

#### Q12: "Why did you choose Vanilla CSS and Glassmorphism instead of Tailwind or Bootstrap?"
> **Answer**: "Tailwind and Bootstrap introduce substantial CSS bundle sizes and often produce generic corporate interfaces. For student mental health, visual immersion and warmth are critical. We created a custom Glassmorphic dark cyberpunk design system using CSS backdrop filters, neon gradients, and responsive flex/grid layouts with zero external UI dependencies."

#### Q13: "What is the Wellness Index formula?"
> **Answer**: "The Wellness Index is a normalized 0–100 score calculated by combining weighted factors:
> $$\text{Wellness Index} = 100 - (w_1 \cdot \text{Sleep Deficit}) - (w_2 \cdot \text{Workload Ratio}) - (w_3 \cdot \text{Screen Penalty}) - (w_4 \cdot \text{Negative Sentiment})$$
> Scores above 70 indicate healthy balance, 45–69 indicate moderate strain, and below 45 indicate elevated risk."

#### Q14: "What were your individual contributions?"
> **Answer**:
> - **Anand Singh Rathore**: Architected the backend Flask microservice, JWT authentication pipelines, Groq Llama 3.3 LLM orchestrator, CrisisHandler safety interceptor, and wrote the automated Pytest testing suite.
> - **Diksha Shekhawat**: Integrated the DistilBERT NLP models, designed the Google Places API geolocation and Haversine spatial referral engine, built the 30-Day Mood Stability Heatmap, and led the frontend glassmorphism UI design."

#### Q15: "What are the key limitations and what is your future scope?"
> **Answer**: "Currently, AIRA is a web platform relying on self-reported inputs and text entries. In our future scope, we plan to develop a React Native mobile application for daily push check-ins, integrate smartwatch sensors to capture real-time physiological indicators like Heart Rate Variability (HRV), and implement WebRTC encrypted video counseling."

---

## 🏆 Checklist for the Presentation Day
- [ ] Ensure Flask backend is running on `http://127.0.0.1:5000/`.
- [ ] Ensure Vite frontend is running on `http://localhost:3000/`.
- [ ] Keep terminal open in a clean tab with `pytest backend/tests/test_pytest_unit.py` ready to run.
- [ ] Have `PRESENTATION_README.md` and `docs/Final_Report.docx` ready on your desktop.
- [ ] Grant browser location permission in advance for instant doctor card rendering.
- [ ] Speak clearly, divide speaking parts equally with your teammate, and project confidence!
