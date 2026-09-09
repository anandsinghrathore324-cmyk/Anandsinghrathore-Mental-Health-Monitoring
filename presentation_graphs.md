# 📊 AIRA Presentation Graphs Visual Gallery

Below are all **6 publication-grade (300 DPI) visual charts** generated directly from your project's empirical datasets, machine learning models, and algorithms.

---

## 📈 1. Multi-Model Benchmark Comparison (Accuracy, Recall, Precision, F1, ROC-AUC)

![Model Benchmark Comparison](C:/Users/ajays/.gemini/antigravity-ide/brain/a6ec33d8-67cc-46bb-914a-e1e78939de67/1_model_performance_comparison.png)

### Key Metrics Summary Table:
| Metric | 🥇 **Logistic Regression** (Chosen) | 🥈 **XGBoost** | 🥉 **Random Forest** |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **79.82%** | 78.73% | 77.39% |
| **Precision** | **81.28%** | 80.76% | 80.19% |
| **Recall (Sensitivity)** | **85.16%** *(Winner)* | 83.60% | 81.52% |
| **F1-Score** | **83.17%** | 82.15% | 80.85% |
| **ROC-AUC Score** | **86.66%** | 85.37% | 84.44% |

---

## 🧩 2. Confusion Matrices Comparison (5,581 Test Samples)

![Confusion Matrices Comparison](C:/Users/ajays/.gemini/antigravity-ide/brain/a6ec33d8-67cc-46bb-914a-e1e78939de67/2_confusion_matrices_comparison.png)

> [!IMPORTANT]
> **Why this wins the defense**: Notice the bottom-left quadrant (False Negatives — distressed students who are missed).
> * **Logistic Regression**: Only **485 missed** *(Lowest / Best clinical safety)*.
> * **XGBoost**: 536 missed.
> * **Random Forest**: 604 missed.

---

## 📉 3. Receiver Operating Characteristic (ROC-AUC) Curves

![ROC-AUC Curves](C:/Users/ajays/.gemini/antigravity-ide/brain/a6ec33d8-67cc-46bb-914a-e1e78939de67/3_roc_auc_curves.png)

* **Logistic Regression**: **AUC = 0.8666** (Superior discrimination threshold)
* **XGBoost**: AUC = 0.8537
* **Random Forest**: AUC = 0.8444
* **Random Guess Baseline**: AUC = 0.5000

---

## 📊 4. Behavioral Stress Drivers Correlation (N = 27,901 Students)

![Behavioral Stress Correlation](C:/Users/ajays/.gemini/antigravity-ide/brain/a6ec33d8-67cc-46bb-914a-e1e78939de67/4_feature_importance_correlation.png)

* **Strongest Distress Accelerators**:
  - **Academic Pressure**: $r = +0.435$
  - **Financial Stress**: $r = +0.312$
  - **Daily Work/Study Hours**: $r = +0.285$
* **Strongest Protective Buffer**:
  - **Study Satisfaction**: $r = -0.320$

---

## 🎭 5. DistilBERT NLP Multi-Class Emotion Analysis

![DistilBERT Emotion Analysis](C:/Users/ajays/.gemini/antigravity-ide/brain/a6ec33d8-67cc-46bb-914a-e1e78939de67/5_distilbert_emotion_analysis.png)

* Compares a **Distressed Student Journal** (Sadness: 42.5%, Fear/Anxiety: 38.2%) vs. a **Balanced Student Journal** (Joy: 56.5%, Love: 24.3%).
* High sadness and fear trigger the automatic `CrisisHandler` de-escalation safety protocol and 24/7 helpline buttons (Tele-MANAS & KIRAN).

---

## 🌐 6. Spatial Haversine Distance & 100 km Safe Radius Boundary

![Spatial Haversine Model](C:/Users/ajays/.gemini/antigravity-ide/brain/a6ec33d8-67cc-46bb-914a-e1e78939de67/6_spatial_haversine_radius.png)

* Illustrates the **100-kilometer strict cutoff boundary** enforced by our Haversine algorithm during Google Places API fallbacks, preventing out-of-state clinic leakage.
