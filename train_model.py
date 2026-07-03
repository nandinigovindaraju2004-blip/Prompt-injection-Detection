"""
train_model.py
----------------
Trains the Prompt Injection Detection classifier.

Pipeline:
  1. Load labeled dataset (dataset/prompts.csv)
  2. Clean + preprocess text
  3. TF-IDF vectorization
  4. Train Logistic Regression + Random Forest
  5. Evaluate both, pick the best (or ensemble)
  6. Save vectorizer + model to server/ml/model_artifacts/

Run:
  pip install scikit-learn pandas numpy joblib --break-system-packages
  python notebooks/train_model.py
"""

import re
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "prompts.csv")
ARTIFACT_DIR = os.path.join(BASE_DIR, "server", "ml", "model_artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    df = pd.read_csv(DATASET_PATH)
    df["clean_text"] = df["text"].apply(clean_text)

    X = df["clean_text"]
    y = df["label"].map({"safe": 0, "malicious": 1})

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced"),
    }

    results = {}
    best_model_name, best_model, best_acc = None, None, -1

    for name, model in models.items():
        model.fit(X_train_vec, y_train)
        preds = model.predict(X_test_vec)
        acc = accuracy_score(y_test, preds)
        report = classification_report(y_test, preds, target_names=["safe", "malicious"], output_dict=True)
        results[name] = {"accuracy": acc, "report": report}
        print(f"\n=== {name} ===")
        print(f"Accuracy: {acc:.4f}")
        print(classification_report(y_test, preds, target_names=["safe", "malicious"]))
        print("Confusion matrix:\n", confusion_matrix(y_test, preds))

        if acc > best_acc:
            best_acc = acc
            best_model_name = name
            best_model = model

    print(f"\nBest model: {best_model_name} (accuracy={best_acc:.4f})")

    # Save artifacts
    joblib.dump(vectorizer, os.path.join(ARTIFACT_DIR, "tfidf_vectorizer.joblib"))
    joblib.dump(best_model, os.path.join(ARTIFACT_DIR, "classifier.joblib"))

    with open(os.path.join(ARTIFACT_DIR, "metadata.json"), "w") as f:
        json.dump({
            "best_model": best_model_name,
            "accuracy": best_acc,
            "label_map": {"0": "safe", "1": "malicious"},
            "results_summary": {k: v["accuracy"] for k, v in results.items()},
        }, f, indent=2)

    print(f"\nSaved model artifacts to: {ARTIFACT_DIR}")


if __name__ == "__main__":
    main()
