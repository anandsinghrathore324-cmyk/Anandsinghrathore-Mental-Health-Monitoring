import os
import re
import pickle
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
    cm = confusion_matrix(y_test, y_pred)
    
    # Extract TN, FP, FN, TP
    tn, fp, fn, tp = cm.ravel()
    
    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        }
    }

def main():
    print("Loading data...")
    path = os.path.join("data", "mental-health-corpus", "mental_health.csv")
    df = pd.read_csv(path)
    
    print("Cleaning text...")
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    print("Splitting train/test...")
    train_df, test_df = train_test_split(df, test_size=0.20, random_state=42, stratify=df['label'])
    
    # Load the vectorizer
    print("Loading TF-IDF vectorizer...")
    with open("text_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
        
    print("Transforming text features...")
    X_train = vectorizer.transform(train_df['cleaned_text'])
    X_test = vectorizer.transform(test_df['cleaned_text'])
    y_train = train_df['label'].values
    y_test = test_df['label'].values
    
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Linear SVM": LinearSVC(random_state=42, dual=False),
        "Multinomial Naive Bayes": MultinomialNB()
    }
    
    results = {}
    
    for name, clf in models.items():
        print(f"Training {name}...")
        clf.fit(X_train, y_train)
        print(f"Evaluating {name}...")
        results[name] = evaluate_model(clf, X_test, y_test)
        
    print("\nTraining Comparison:")
    for name, metrics in results.items():
        print(f"{name}:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1 Score:  {metrics['f1_score']:.4f}")
        print(f"  CM (TN, FP, FN, TP): {[metrics['confusion_matrix']['tn'], metrics['confusion_matrix']['fp'], metrics['confusion_matrix']['fn'], metrics['confusion_matrix']['tp']]}")
        
    # Select best model based on F1 Score (primary) and Recall (secondary)
    best_name = None
    best_f1 = -1
    best_recall = -1
    
    for name, metrics in results.items():
        f1 = metrics["f1_score"]
        rec = metrics["recall"]
        if f1 > best_f1:
            best_f1 = f1
            best_recall = rec
            best_name = name
        elif abs(f1 - best_f1) < 1e-6 and rec > best_recall:
            best_recall = rec
            best_name = name
            
    print(f"\nBest Model Selected: {best_name} (F1 Score: {best_f1:.4f}, Recall: {best_recall:.4f})")
    
    # Save the best model
    best_clf = models[best_name]
    model_path = "text_model.pkl"
    print(f"Saving best model to {model_path}...")
    with open(model_path, "wb") as f:
        pickle.dump(best_clf, f)
        
    # Save statistics for the report
    scratch_dir = r"C:\Users\ajays\.gemini\antigravity-ide\brain\4cc7fc5f-0cb3-4c5c-b23b-630f4fbfff59\scratch"
    os.makedirs(scratch_dir, exist_ok=True)
    report_data_path = os.path.join(scratch_dir, "model_training_stats.json")
    with open(report_data_path, "w") as f:
        json.dump({
            "results": results,
            "best_model": {
                "name": best_name,
                "f1_score": best_f1,
                "recall": best_recall,
                "path": model_path
            }
        }, f, indent=4)
        
    print(f"Training stats saved to {report_data_path}")

if __name__ == "__main__":
    main()
