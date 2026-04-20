import csv
from pathlib import Path

from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

DATA_FILE = Path("news_dataset.csv")
MODEL_FILE = Path("model.joblib")

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset file not found: {DATA_FILE}")

texts = []
labels = []
with DATA_FILE.open(newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        texts.append(row["text"])
        labels.append(row["label"])

pipeline = Pipeline(
    [
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english")),
        ("clf", LogisticRegression(max_iter=500, solver="liblinear")),
    ]
)

pipeline.fit(texts, labels)
dump(pipeline, MODEL_FILE)
print(f"Model trained and saved to {MODEL_FILE}")
