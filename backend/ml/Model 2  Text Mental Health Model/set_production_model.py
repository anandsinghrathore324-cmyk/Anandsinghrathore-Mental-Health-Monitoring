import os
import re
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    print("Loading Mental Health Corpus...")
    path = os.path.join("data", "mental-health-corpus", "mental_health.csv")
    df = pd.read_csv(path)
    
    print("Cleaning text...")
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    print("Splitting train/test...")
    train_df, test_df = train_test_split(df, test_size=0.20, random_state=42, stratify=df['label'])
    
    print("Loading TF-IDF vectorizer...")
    with open("text_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
        
    print("Extracting features...")
    X_train = vectorizer.transform(train_df['cleaned_text'])
    y_train = train_df['label'].values
    
    print("Training Logistic Regression for production...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    
    model_path = "text_model.pkl"
    print(f"Saving Logistic Regression model to {model_path}...")
    with open(model_path, "wb") as f:
        pickle.dump(lr_model, f)
        
    print("Production-ready model successfully saved!")

if __name__ == "__main__":
    main()
