import os
import re
import pickle
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # 1. Lowercase
    text = text.lower()
    # 2. Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # 3. Remove special characters (keep alphanumeric and spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # 4. Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    print("Loading Mental Health Corpus...")
    path = os.path.join("data", "mental-health-corpus", "mental_health.csv")
    df = pd.read_csv(path)
    
    # 1. Basic properties
    total_records = len(df)
    class_counts = df['label'].value_counts().to_dict()
    
    # 2. Analyze raw text lengths
    df['raw_char_len'] = df['text'].astype(str).apply(len)
    df['raw_word_count'] = df['text'].astype(str).apply(lambda x: len(x.split()))
    
    raw_stats = {
        "char_len": {
            "mean": df['raw_char_len'].mean(),
            "min": int(df['raw_char_len'].min()),
            "max": int(df['raw_char_len'].max()),
            "median": df['raw_char_len'].median()
        },
        "word_count": {
            "mean": df['raw_word_count'].mean(),
            "min": int(df['raw_word_count'].min()),
            "max": int(df['raw_word_count'].max()),
            "median": df['raw_word_count'].median()
        }
    }
    
    # Text length distribution by class
    class_raw_stats = {}
    for cls in df['label'].unique():
        sub = df[df['label'] == cls]
        class_raw_stats[str(cls)] = {
            "mean_char_len": sub['raw_char_len'].mean(),
            "mean_word_count": sub['raw_word_count'].mean()
        }
        
    # 3. Clean Text
    print("Cleaning text (lowercase, removing URLs, special characters, extra spaces)...")
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    # Analyze cleaned text lengths
    df['clean_char_len'] = df['cleaned_text'].apply(len)
    df['clean_word_count'] = df['cleaned_text'].apply(lambda x: len(x.split()))
    
    clean_stats = {
        "char_len": {
            "mean": df['clean_char_len'].mean(),
            "min": int(df['clean_char_len'].min()),
            "max": int(df['clean_char_len'].max()),
            "median": df['clean_char_len'].median()
        },
        "word_count": {
            "mean": df['clean_word_count'].mean(),
            "min": int(df['clean_word_count'].min()),
            "max": int(df['clean_word_count'].max()),
            "median": df['clean_word_count'].median()
        }
    }
    
    # 4. Split Train/Test (80/20)
    print("Splitting into train/test sets...")
    train_df, test_df = train_test_split(df, test_size=0.20, random_state=42, stratify=df['label'])
    
    train_size = len(train_df)
    test_size = len(test_df)
    
    # 5. TF-IDF features
    print("Creating TF-IDF features...")
    # Using 10,000 max features, sublinear TF scaling, and standard english stop words
    vectorizer = TfidfVectorizer(max_features=10000, stop_words='english', sublinear_tf=True)
    X_train_tfidf = vectorizer.fit_transform(train_df['cleaned_text'])
    
    # 6. Save Vectorizer
    vectorizer_path = "text_vectorizer.pkl"
    print(f"Saving vectorizer to {vectorizer_path}...")
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
        
    # Output stats for reporting
    stats = {
        "total_records": total_records,
        "class_counts": class_counts,
        "train_size": train_size,
        "test_size": test_size,
        "vocab_size": len(vectorizer.vocabulary_),
        "raw_stats": raw_stats,
        "class_raw_stats": class_raw_stats,
        "clean_stats": clean_stats
    }
    
    # Write to temp folder for agent retrieval
    scratch_dir = r"C:\Users\ajays\.gemini\antigravity-ide\brain\4cc7fc5f-0cb3-4c5c-b23b-630f4fbfff59\scratch"
    os.makedirs(scratch_dir, exist_ok=True)
    stats_path = os.path.join(scratch_dir, "eda_prep_stats.json")
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=4)
        
    print(f"Stats written to {stats_path}")
    print("Preprocessing completed successfully!")

if __name__ == "__main__":
    main()
