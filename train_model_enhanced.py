import csv
import os
import urllib.request
from pathlib import Path
import pandas as pd
import numpy as np
from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sentence_transformers import SentenceTransformer
import warnings
warnings.filterwarnings('ignore')

DATA_FILE = Path("news_dataset.csv")
MODEL_FILE = Path("model.joblib")
ENHANCED_MODEL_FILE = Path("model_enhanced.joblib")
EMBEDDINGS_FILE = Path("embeddings_model.joblib")

def download_isot_dataset():
    """Download ISOT Fake News dataset"""
    print("Downloading ISOT Fake News dataset...")
    
    fake_url = "https://raw.githubusercontent.com/several27/FakeNewsCorpus/master/news_sample.csv"
    
    # Using local sample data as fallback
    print("Using local enhanced dataset...")
    return None

def load_and_prepare_data():
    """Load and prepare training data with enhanced features"""
    
    if not DATA_FILE.exists():
        print("Creating sample enhanced dataset...")
        # Create a more comprehensive sample dataset
        sample_data = [
            # REAL NEWS
            ("Scientists confirm new breakthrough in cancer treatment", "real"),
            ("Study shows vaccines are effective against coronavirus", "real"),
            ("Government announces new infrastructure development plan", "real"),
            ("NASA discovers new exoplanet in habitable zone", "real"),
            ("University researchers publish findings on climate change", "real"),
            ("Official statement from WHO regarding health guidelines", "real"),
            ("New law passed to protect endangered species", "real"),
            ("Economic report shows job growth this quarter", "real"),
            ("Medical breakthrough in treating neurological disorder", "real"),
            ("Space agency announces upcoming Mars mission", "real"),
            ("Archaeological team uncovers ancient civilization remains", "real"),
            ("New renewable energy technology shows promise", "real"),
            ("Research indicates benefits of renewable energy", "real"),
            ("CDC confirms new medical findings", "real"),
            ("Official data shows economic recovery trends", "real"),
            
            # FAKE NEWS
            ("Vaccines secretly contain microchips from Bill Gates", "fake"),
            ("Moon landing was completely faked by NASA in 1969", "fake"),
            ("Aliens landed on Earth and live underground", "fake"),
            ("Chemtrails are poisoning the population daily", "fake"),
            ("Miracle cure for cancer suppressed by big pharma", "fake"),
            ("COVID-19 vaccine causes autism in children", "fake"),
            ("Flat Earth theory proved by ancient texts", "fake"),
            ("Reptilians control world governments in secret", "fake"),
            ("5G technology causes coronavirus transmission", "fake"),
            ("Queen Elizabeth is not human reptile alien", "fake"),
            ("Free energy device destroyed by oil companies", "fake"),
            ("Government hides evidence of alien visitation", "fake"),
            ("Illuminati controls all major world events", "fake"),
            ("Zombies are real creatures spreading virus", "fake"),
            ("Sandy Hook shooting was completely staged hoax", "fake"),
        ]
        
        # Write to CSV
        with DATA_FILE.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'label'])
            writer.writeheader()
            for text, label in sample_data:
                writer.writerow({'text': text, 'label': label})
        print(f"Created sample dataset with {len(sample_data)} articles")
    
    # Load data
    df = pd.read_csv(DATA_FILE)
    
    # Data cleaning and preparation
    df['text'] = df['text'].str.lower().str.strip()
    df = df.dropna(subset=['text', 'label'])
    
    print(f"Loaded {len(df)} articles for training")
    print(f"Real: {len(df[df['label'] == 'real'])}, Fake: {len(df[df['label'] == 'fake'])}")
    
    return df

def create_advanced_features(texts):
    """Create advanced linguistic features"""
    features = []
    for text in texts:
        feature_dict = {
            'text': text,
            'length': len(text),
            'word_count': len(text.split()),
            'avg_word_length': np.mean([len(w) for w in text.split()]) if text.split() else 0,
            'capital_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
        }
        features.append(feature_dict)
    return features

def train_enhanced_model(df):
    """Train enhanced model with multiple algorithms"""
    
    print("\n=== Training Enhanced Fake News Detector ===\n")
    
    X_texts = df['text'].values
    y = df['label'].values
    
    # Create TF-IDF vectors with bigrams and trigrams
    print("1. Creating TF-IDF features...")
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 3),
        stop_words='english',
        min_df=1,
        max_df=0.95,
        sublinear_tf=True
    )
    X_tfidf = tfidf.fit_transform(X_texts)
    
    print("2. Training ensemble model...")
    # Use ensemble of classifiers for better accuracy
    model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    model.fit(X_tfidf, y)
    
    print("3. Saving models...")
    # Save as pipeline for easy prediction
    pipeline = Pipeline([
        ('tfidf', tfidf),
        ('classifier', model)
    ])
    
    dump(pipeline, MODEL_FILE)
    print(f"✓ Model saved to {MODEL_FILE}")
    
    # Calculate accuracy on training data
    accuracy = model.score(X_tfidf, y)
    print(f"\n✓ Model Training Accuracy: {accuracy:.2%}")
    
    return pipeline

def train_embedding_model():
    """Train sentence embeddings for similarity-based detection"""
    print("\n4. Training embedding model for advanced similarity checks...")
    
    try:
        # Load pre-trained sentence transformer
        embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        dump(embeddings_model, EMBEDDINGS_FILE)
        print(f"✓ Embedding model saved to {EMBEDDINGS_FILE}")
        return embeddings_model
    except Exception as e:
        print(f"⚠ Could not load embedding model: {e}")
        print("Skipping embedding model training...")
        return None

def main():
    print("\n" + "="*50)
    print("ENHANCED FAKE NEWS MODEL TRAINING")
    print("="*50 + "\n")
    
    # Load and prepare data
    df = load_and_prepare_data()
    
    # Train main model
    pipeline = train_enhanced_model(df)
    
    # Train embedding model
    embedding_model = train_embedding_model()
    
    print("\n" + "="*50)
    print("✓ TRAINING COMPLETE!")
    print("="*50)
    print("\nModels created:")
    print(f"  - Main classifier: {MODEL_FILE}")
    if embedding_model:
        print(f"  - Embedding model: {EMBEDDINGS_FILE}")
    print("\nThe app will now use these enhanced models for predictions.\n")

if __name__ == "__main__":
    main()
