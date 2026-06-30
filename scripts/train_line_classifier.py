"""
Train a simple line-level classifier to distinguish `education` vs `experience` lines.

Usage:
  - Prepare a labeled CSV at `outputs/labeling_labeled.csv` with columns: `line_text,label` (label values: education|experience|other)
  - Run: `python scripts/train_line_classifier.py`

This script trains a TF-IDF + LogisticRegression model and saves it to `models/line_classifier.joblib`.
"""
import os
import argparse
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib


ROOT = Path(os.getcwd())
OUT_DIR = ROOT / 'outputs'
MODELS_DIR = ROOT / 'models'
MODELS_DIR.mkdir(exist_ok=True)


def main():
    labeled = OUT_DIR / 'labeling_labeled.csv'
    if not labeled.exists():
        print('Expected labeled CSV at', labeled)
        return

    df = pd.read_csv(labeled)
    df = df.dropna(subset=['line_text','label'])
    X = df['line_text'].astype(str)
    y = df['label'].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1,2), min_df=2)),
        ('clf', LogisticRegression(max_iter=1000))
    ])

    print('Training classifier on', len(X_train), 'examples')
    pipe.fit(X_train, y_train)

    preds = pipe.predict(X_test)
    print(classification_report(y_test, preds))

    # cross-val
    scores = cross_val_score(pipe, X, y, cv=5, scoring='f1_macro')
    print('5-fold F1-macro:', scores.mean(), scores)

    model_path = MODELS_DIR / 'line_classifier.joblib'
    joblib.dump(pipe, model_path)
    print('Saved model to', model_path)


if __name__ == '__main__':
    main()
