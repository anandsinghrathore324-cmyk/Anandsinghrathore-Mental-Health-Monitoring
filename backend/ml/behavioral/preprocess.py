import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# 1. Load dataset
data_dir = os.path.join(os.path.dirname(__file__), "data")
data_path = os.path.join(data_dir, "Student Depression Dataset.csv")
if not os.path.exists(data_path):
    data_path = "Student Depression Dataset.csv"
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Dataset not found at {data_path}")

df = pd.read_csv(data_path)

# Features and target defined by user
features = [
    "Age",
    "Gender",
    "Academic Pressure",
    "Study Satisfaction",
    "Sleep Duration",
    "Dietary Habits",
    "Work/Study Hours",
    "Financial Stress",
    "Family History of Mental Illness"
]
target = "Depression"

# Keep only specified features and target
df_subset = df[features + [target]].copy()

# Split X and y
X = df_subset[features]
y = df_subset[target]

# Define columns by type
numeric_features = [
    "Age",
    "Academic Pressure",
    "Study Satisfaction",
    "Work/Study Hours",
    "Financial Stress"
]
categorical_features = [
    "Gender",
    "Sleep Duration",
    "Dietary Habits",
    "Family History of Mental Illness"
]

# 2. Define pipelines for numerical and categorical features
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

# Combine into a ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

# Fit the preprocessor on the whole feature set or training set
# We fit on the training set to prevent data leakage.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

print(f"Original X shape: {X.shape}")
print(f"Train set shape: {X_train.shape}, Test set shape: {X_test.shape}")

# Fit and transform training data
X_train_preprocessed = preprocessor.fit_transform(X_train)
X_test_preprocessed = preprocessor.transform(X_test)

# Get feature names after one-hot encoding
cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
encoded_cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
all_feature_names = numeric_features + encoded_cat_names

# Convert back to DataFrame for visibility
X_train_preprocessed_df = pd.DataFrame(X_train_preprocessed, columns=all_feature_names)
X_test_preprocessed_df = pd.DataFrame(X_test_preprocessed, columns=all_feature_names)

print(f"Preprocessed Train shape: {X_train_preprocessed_df.shape}")
print(f"Preprocessed Test shape: {X_test_preprocessed_df.shape}")
print("\nFirst 3 rows of preprocessed training data:")
print(X_train_preprocessed_df.head(3).to_string())

# 6. Save preprocessing objects and datasets for future use
os.makedirs("preprocessed", exist_ok=True)
joblib.dump(preprocessor, "preprocessed/preprocessor.joblib")

# Save processed datasets
X_train_preprocessed_df.to_csv("preprocessed/X_train.csv", index=False)
X_test_preprocessed_df.to_csv("preprocessed/X_test.csv", index=False)
y_train.to_csv("preprocessed/y_train.csv", index=False)
y_test.to_csv("preprocessed/y_test.csv", index=False)

print("\nSaved preprocessor to 'preprocessed/preprocessor.joblib'")
print("Saved preprocessed train/test splits to 'preprocessed/' directory.")
