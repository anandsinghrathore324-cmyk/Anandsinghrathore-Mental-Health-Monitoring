import os
import sys
import pandas as pd
import numpy as np
import pickle
import json

# Ensure necessary libraries are installed
try:
    import xgboost as xgb
except ImportError:
    print("xgboost not found. Attempting to install...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "xgboost"])
    import xgboost as xgb

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
)

# 1. Load the preprocessed datasets
X_train = pd.read_csv("preprocessed/X_train.csv")
X_test = pd.read_csv("preprocessed/X_test.csv")
y_train = pd.read_csv("preprocessed/y_train.csv").values.ravel()
y_test = pd.read_csv("preprocessed/y_test.csv").values.ravel()

# 2. Define the models to train
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    "XGBoost": xgb.XGBClassifier(eval_metric='logloss', random_state=42, n_jobs=-1)
}

# 3. Train and evaluate each model
results = {}
trained_models = {}

for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)
    trained_models[name] = model
    
    # Predict
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred
    
    # Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    cm = confusion_matrix(y_test, y_pred).tolist() # [[TN, FP], [FN, TP]]
    
    results[name] = {
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1 Score": f1,
        "ROC-AUC Score": roc_auc,
        "Confusion Matrix": cm
    }

# Print the comparison table in console format
print("\nComparison Results:")
print(pd.DataFrame(results).T.to_string())

# 4. Select the best performing model
# We will select the best model based on F1 Score or ROC-AUC. Let's use F1 Score as it balances precision and recall.
best_model_name = max(results, key=lambda k: results[k]["F1 Score"])
best_model = trained_models[best_model_name]
print(f"\nBest performing model based on F1 Score: {best_model_name}")

# 5. Save the best model
os.makedirs("models", exist_ok=True)
model_path = "models/risk_model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(best_model, f)
print(f"Saved best model to '{model_path}'")

# 6. Save a model performance report
report = {
    "comparison_results": results,
    "best_model_name": best_model_name,
    "best_model_metrics": results[best_model_name]
}

report_path = "models/model_performance_report.json"
with open(report_path, "w") as f:
    json.dump(report, f, indent=4)
print(f"Saved performance report to '{report_path}'")
