# PRACTICE SCHOOL – I FINAL REPORT
## AIRA: AI-Based Student Mental Health Monitoring and Support System

**Degree**: Bachelor of Technology in Computer Science Engineering  
**Institution**: Department of Computer Science Engineering, Institute of Engineering and Technology, JK Lakshmipat University, Jaipur  
**Date**: August 2026  

---

### PREPARED BY:
- **Diksha Shekhawat** (Roll No: 2024BTECH156)
- **Anand Singh Rathore** (Roll No: 2024BTECH158)

### SUPERVISORS:
- **Faculty Supervisors**: Dr. Sonali Vyas & Dr. Rajnish Kumar
- **External Supervisor**: Dr. Saurabh Kumar

---

## CERTIFICATE OF WORK COMPLETION
This is to certify that the Practice School-I project report entitled **"AIRA: AI-Based Student Mental Health Monitoring and Support System"** submitted by **Diksha Shekhawat (2024BTECH156)** and **Anand Singh Rathore (2024BTECH158)** towards the partial fulfillment of the requirements for the degree of Bachelor of Technology in Computer Science Engineering of JK Lakshmipat University, Jaipur, is an authentic record of work carried out by them under our supervision and guidance.

In our opinion, the submitted work has reached the required academic and technical standard for being accepted for the Practice School-I examination.

---

## ACKNOWLEDGEMENTS
We express our profound gratitude to our supervisors Dr. Sonali Vyas, Dr. Rajnish Kumar, and Dr. Saurabh Kumar for their continuous academic supervision, constructive feedback, and architectural evaluation throughout the development of the AIRA platform.

---

## ABSTRACT
Student mental health is a critical concern in modern higher education. AIRA is an intelligent full-stack web platform designed to detect early emotional distress, analyze behavioral patterns, provide real-time AI conversational support, and dynamically connect students to verified local mental health specialists.

AIRA integrates dual machine learning prediction engines (DistilBERT NLP sentiment analysis + Behavioral ML regression), a responsive cyberpunk-themed interface, a 30-Day Mood Heatmap, an empathetic AI Chatbot Assistant, and a dynamic Geolocation Specialist Referral module powered by the Google Places API (New) and browser HTML5 GPS location auto-detection with spatial Haversine distance calculations.

System reliability is empirically verified through an automated test suite comprising 175 unit and integration tests (100% pass rate).

---

## TABLE OF CONTENTS
1. Introduction & Project Vision
2. Progress from Milestone Stage
3. System Architecture & Technical Implementation
   - 3.1 Machine Learning Diagnostic Models (NLP & Behavioral Regression)
   - 3.2 AIRA Chatbot Orchestrator & Contextual Memory System
   - 3.3 Live Google Places API Geolocation & Spatial Haversine Distance Engine
   - 3.4 Database Architecture & MongoDB Indexing Schemas
   - 3.5 Security Policies & Brevo REST API Email Driver
4. Empirical Quality Assurance & Automated Test Suite (175 Tests)
5. Key Learnings & Engineering Challenges Solved
6. Conclusion & Future Scope
7. References

---

## 1. INTRODUCTION & PROJECT VISION
University and high-school students routinely experience acute stress, anxiety disorders, and depression driven by academic load and lifestyle imbalances. AIRA provides a non-invasive, accessible digital wellness environment offering real-time AI diagnostics, empathetic chatbot support, and live specialist referrals.

---

## 2. PROGRESS FROM MILESTONE STAGE
| Module / Feature | Milestone Prototype Status | Final Phase Completed Status |
| :--- | :--- | :--- |
| **AI Diagnostic Engine** | Unintegrated static risk scores | Integrated DistilBERT NLP + Behavioral ML Regression |
| **AIRA Chatbot Assistant** | Basic keyword rule responses | Contextual memory orchestrator with crisis detection |
| **Geolocation & Doctor Search** | Hardcoded static coordinate lists | Live Google Places API + HTML5 GPS + Haversine distance engine |
| **Quality Assurance & Testing** | Manual ad-hoc testing | 175 automated unit and integration tests (100% pass rate) |

---

## 3. SYSTEM ARCHITECTURE & TECHNICAL IMPLEMENTATION
AIRA is built on a decoupled full-stack architecture:
- **Frontend**: Vanilla HTML5, CSS3 Glassmorphic UI, Vanilla ES6+ JS.
- **Backend**: Python 3.12, Flask Framework, PyJWT, Bcrypt, Brevo REST API.
- **Machine Learning**: Fine-tuned DistilBERT NLP transformer + Behavioral ML Regression model.
- **Geolocation**: Live Google Places API (New) (`places.googleapis.com/v1/places:searchText`), Browser HTML5 Geolocation (`navigator.geolocation`), Haversine distance calculation, dynamic SVG avatars (`ui-avatars.com`).
- **Database**: MongoDB with programmatic indexing on users, mental health reports, mood logs, OTP codes (TTL 5 mins), and doctor recommendations.

---

## 4. EMPIRICAL QUALITY ASSURANCE & AUTOMATED TEST SUITE
System stability is backed by an automated pytest suite:
- **Total Executed Tests**: 175 Tests
- **Pass Rate**: 100% (175 Passed, 0 Failed)
- **Execution Time**: ~20.67 Seconds

---

## 5. KEY LEARNINGS & ENGINEERING CHALLENGES SOLVED
- **Google Places API Quota Management (HTTP 429)**: Implemented Haversine distance calculations on fallback database records, strictly capping distance to `<= 100 km` to prevent distant location leakage.
- **Cloud SMTP Port Blocking**: Solved Render SMTP port restrictions by building a custom Brevo REST API driver over HTTPS (port 443).

---

## 6. CONCLUSION & FUTURE SCOPE
AIRA is a fully functional, empirically verified, and production-ready mental health monitoring platform. Future scope includes native mobile applications (React Native), smartwatch HRV wearable integration, and WebRTC video counseling.

---

## 7. REFERENCES
- Brevo API v3 Documentation: https://developers.brevo.com/docs
- Flask Web Framework: https://flask.palletsprojects.com
- Google Places API (New): https://developers.google.com/maps/documentation/places/web-service
- Hugging Face Transformers & DistilBERT: https://huggingface.co/docs/transformers
- Pytest Documentation: https://docs.pytest.org
