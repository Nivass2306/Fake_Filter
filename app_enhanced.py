from datetime import datetime, timezone
from pathlib import Path
import re
import requests
import os
from bs4 import BeautifulSoup
import webbrowser
import threading
import time
import json
import warnings
warnings.filterwarnings('ignore')

from flask import Flask, jsonify, render_template, request
from joblib import load

app = Flask(__name__)

# Model paths
MODEL_PATH = Path("model.joblib")
MODEL_ENHANCED_PATH = Path("model_enhanced.joblib")
EMBEDDINGS_PATH = Path("embeddings_model.joblib")

model = None
embeddings_model = None
model_status = "No trained model available. Use train_model_enhanced.py to generate one."

# Enhanced keywords with severity scores
fake_keywords = {
    # Conspiracy theories (high priority)
    "microchip": 0.9, "bill gates": 0.9, "illuminati": 0.9, "reptilian": 0.9,
    "chemtrails": 0.85, "moon landing fake": 0.85, "flat earth": 0.8,
    # Health misinformation
    "vaccines cause autism": 0.95, "5g coronavirus": 0.9, "miracle cure": 0.85,
    # Hoaxes
    "hoax": 0.7, "fake": 0.7, "false": 0.6, "rumor": 0.6, "fabricated": 0.8,
    # Misleading
    "clickbait": 0.6, "misleading": 0.65, "scam": 0.75, "unverified": 0.5,
}

reliable_keywords = {
    # Sources
    "study": 0.8, "research": 0.8, "according to": 0.7, "report": 0.75,
    "confirmed": 0.85, "verified": 0.85, "official": 0.8, "data": 0.75,
    # Credible sources
    "nasa": 0.95, "cdc": 0.95, "who": 0.95, "university": 0.85, "government": 0.75,
    "scientific": 0.9, "peer reviewed": 0.95, "clinical trial": 0.9,
}

# Fact-checking database with verified information
fact_check_db = {
    "vaccine autism": {
        "verdict": "fake",
        "confidence": 0.99,
        "explanation": "Vaccines do NOT cause autism. This claim has been thoroughly debunked by multiple studies with over 1 million children. The original fraudulent study was retracted.",
        "source": "CDC, WHO, Multiple peer-reviewed studies",
        "link": "https://www.cdc.gov/vaccinesafety/concerns/autism.html"
    },
    "5g coronavirus": {
        "verdict": "fake",
        "confidence": 0.99,
        "explanation": "5G technology does NOT spread COVID-19. Viruses cannot travel on radio waves. COVID-19 spreads through respiratory droplets.",
        "source": "WHO, CDC, International Telecommunications Union",
        "link": "https://www.who.int/news-room/q-a-detail/coronavirus-disease-covid-19-5g-and-covid19"
    },
    "moon landing": {
        "verdict": "fake",
        "confidence": 0.98,
        "explanation": "The Moon landing was real. Apollo 11 landed on the Moon in 1969. Evidence includes moon rocks analyzed by independent scientists, photographs, retroreflectors left on the Moon.",
        "source": "NASA, ESA, Independent Analysis",
        "link": "https://www.nasa.gov/Kennedy/images/content/253261main_ApollinAmerica_FS.pdf"
    },
    "chemtrails": {
        "verdict": "fake",
        "confidence": 0.95,
        "explanation": "Chemtrails are a conspiracy theory. What you see are contrails (condensation trails), water vapor frozen in cold air at high altitude. No evidence of systematic chemical spraying exists.",
        "source": "NOAA, EPA, Scientific Community",
        "link": "https://www.noaa.gov/jetstream/contrails-and-cirrus-clouds"
    },
}

# Suspicious language patterns
suspicious_patterns = [
    r"(doctors (hate|don\'t want you to know)|they don\'t want you to know)",
    r"(secret|hidden|suppressed) (cure|truth|evidence)",
    r"(prove me wrong|fact check this|if this gets deleted)",
    r"(wake up|sheeple|do your own research)",
    r"(100% (guaranteed|proven)|never (lie|fails))",
    r"(leaked document|insider information)",
]

reliable_patterns = [
    r"(study|research|survey) (\w+ )+(found|showed|indicates|suggests)",
    r"(according to|according to the|according to results|based on data)",
    r"(peer.?reviewed|peer.?examined|scientific evidence)",
    r"(government|official) (statement|report|announcement)",
]

def open_browser():
    """Open browser after a short delay to allow server to start"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

def load_model():
    """Load the trained models"""
    global model, embeddings_model, model_status
    
    if MODEL_ENHANCED_PATH.exists():
        try:
            model = load(MODEL_ENHANCED_PATH)
            model_status = "Enhanced ML Model loaded successfully ✓"
            print(f"✓ Loaded enhanced model from {MODEL_ENHANCED_PATH}")
        except Exception as e:
            model_status = f"Error loading enhanced model: {e}"
            print(model_status)
    elif MODEL_PATH.exists():
        try:
            model = load(MODEL_PATH)
            model_status = "ML Model loaded successfully ✓"
            print(f"✓ Loaded model from {MODEL_PATH}")
        except Exception as e:
            model_status = f"Error loading model: {e}"
            print(model_status)
    
    # Load embeddings model if available
    if EMBEDDINGS_PATH.exists():
        try:
            embeddings_model = load(EMBEDDINGS_PATH)
            print(f"✓ Loaded embeddings model from {EMBEDDINGS_PATH}")
        except Exception as e:
            print(f"⚠ Could not load embeddings model: {e}")

def check_with_fact_check_api(text: str) -> dict:
    """Check text against Google Fact Check API"""
    try:
        api_key = os.environ.get('FACT_CHECK_API_KEY', '')  # Set this in environment
        if not api_key:
            return None
        
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            "query": text[:100],  # First 100 chars
            "key": api_key,
            "pageSize": 5
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "claims" in data:
                return data["claims"]
    except Exception as e:
        print(f"API Error: {e}")
    
    return None

def count_keyword_matches(text_lower: str, keyword_dict: dict) -> tuple:
    """Count weighted keyword matches"""
    total_score = 0
    matches = []
    
    for keyword, weight in keyword_dict.items():
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text_lower):
            matches.append(keyword)
            total_score += weight
    
    return total_score, matches

def detect_suspicious_language(text_lower: str) -> tuple:
    """Detect suspicious language patterns"""
    score = 0
    patterns_found = []
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            score += 0.2
            patterns_found.append(pattern[:30] + "...")
    
    return min(score, 1.0), patterns_found

def detect_reliable_patterns(text_lower: str) -> tuple:
    """Detect reliable language patterns"""
    score = 0
    patterns_found = []
    
    for pattern in reliable_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            score += 0.15
            patterns_found.append(pattern[:30] + "...")
    
    return min(score, 1.0), patterns_found

def check_against_fact_db(text_lower: str) -> dict:
    """Check if text matches known false claims"""
    for claim, fact_info in fact_check_db.items():
        if any(word in text_lower for word in claim.split()):
            return fact_info
    return None

def advanced_classification(text: str) -> dict:
    """Hybrid classification using multiple methods"""
    text_lower = text.lower()
    
    # Initialize scores
    ml_score = 0.5
    keyword_score = 0.5
    pattern_score = 0.5
    
    # 1. ML Model prediction (if available)
    if model:
        try:
            prediction = model.predict([text])[0]
            prediction_prob = model.predict_proba([text])[0]
            
            if prediction == "fake":
                ml_score = min(0.7 + prediction_prob[1] * 0.3, 1.0)
            else:
                ml_score = max(0.3 - prediction_prob[0] * 0.3, 0.0)
        except Exception as e:
            print(f"ML prediction error: {e}")
    
    # 2. Keyword analysis
    fake_score, fake_matches = count_keyword_matches(text_lower, fake_keywords)
    reliable_score, reliable_matches = count_keyword_matches(text_lower, reliable_keywords)
    
    # Normalize keyword scores
    keyword_score = fake_score / (fake_score + reliable_score + 0.1)
    
    # 3. Language pattern analysis
    suspicious_score, suspicious_patterns_found = detect_suspicious_language(text_lower)
    reliable_score, reliable_patterns_found = detect_reliable_patterns(text_lower)
    
    pattern_score = (suspicious_score + reliable_score) / 2
    if reliable_score > suspicious_score:
        pattern_score = max(0.1, pattern_score - 0.3)
    
    # 4. Fact database check
    fact_check_result = check_against_fact_db(text_lower)
    if fact_check_result:
        if fact_check_result["verdict"] == "fake":
            keyword_score = max(keyword_score, fact_check_result["confidence"])
        else:
            keyword_score = min(keyword_score, 1 - fact_check_result["confidence"])
    
    # 5. Weighted ensemble (combine all scores)
    final_fake_score = (
        ml_score * 0.35 +
        keyword_score * 0.3 +
        pattern_score * 0.35
    )
    
    # Determine verdict
    if final_fake_score >= 0.7:
        verdict = "Likely Fake"
        confidence = final_fake_score
    elif final_fake_score <= 0.3:
        verdict = "Likely Real"
        confidence = 1 - final_fake_score
    else:
        verdict = "Uncertain"
        confidence = 0.5
    
    return {
        "score": round(final_fake_score * 100),
        "verdict": verdict,
        "confidence": round(confidence * 100),
        "ml_score": round(ml_score * 100) if model else None,
        "keyword_score": round(keyword_score * 100),
        "pattern_score": round(pattern_score * 100),
        "fake_keywords": fake_matches[:5],
        "reliable_keywords": reliable_matches[:5],
        "suspicious_patterns": suspicious_patterns_found[:3],
        "reliable_patterns": reliable_patterns_found[:3],
        "fact_check": fact_check_result,
    }

def get_detailed_explanation(classification_result, original_text):
    """Generate detailed explanation based on classification"""
    text_lower = original_text.lower()
    
    explanation_parts = []
    
    # Base explanation
    if classification_result["verdict"] == "Likely Fake":
        explanation_parts.append(f"🚨 This content scores {classification_result['score']}% fake with {classification_result['confidence']}% confidence.")
        
        if classification_result["fake_keywords"]:
            explanation_parts.append(f"⚠ Suspicious keywords detected: {', '.join(classification_result['fake_keywords'][:3])}")
        
        if classification_result["suspicious_patterns"]:
            explanation_parts.append("🔍 Detected manipulative language patterns that are commonly found in misinformation.")
        
        if classification_result["fact_check"]:
            explanation_parts.append(f"✗ Fact Check: {classification_result['fact_check']['explanation']}")
    
    elif classification_result["verdict"] == "Likely Real":
        explanation_parts.append(f"✓ This content appears reliable ({100-classification_result['score']}% confidence).")
        
        if classification_result["reliable_keywords"]:
            explanation_parts.append(f"✓ Contains reliable sources/language: {', '.join(classification_result['reliable_keywords'][:3])}")
        
        if classification_result["reliable_patterns"]:
            explanation_parts.append("✓ Uses credible reporting language and proper citations.")
    
    else:
        explanation_parts.append(f"❓ Unable to determine reliability. ({classification_result['score']}% fake score)")
        explanation_parts.append("Recommendation: Cross-reference with multiple reliable sources.")
    
    return " ".join(explanation_parts)

def get_related_content(text: str, is_fake: bool) -> dict:
    """Get related content and sources"""
    if is_fake:
        # Return fact-checking resources
        return {
            "type": "fact_check",
            "title": "Check These Fact-Checking Resources",
            "resources": [
                {"name": "Snopes", "url": "https://www.snopes.com", "description": "Long-standing fact-checking database"},
                {"name": "FactCheck.org", "url": "https://www.factcheck.org", "description": "Nonpartisan, nonprofit fact-checker"},
                {"name": "Full Fact", "url": "https://fullfact.org", "description": "UK's independent fact-checking organization"},
                {"name": "Politifact", "url": "https://www.politifact.com", "description": "Political statement fact-checking"},
            ]
        }
    else:
        # Return trustworthy news sources
        return {
            "type": "sources",
            "title": "Verify With These Reliable Sources",
            "resources": [
                {"name": "Reuters", "url": "https://www.reuters.com", "description": "Major international news agency"},
                {"name": "AP News", "url": "https://apnews.com", "description": "Associated Press news"},
                {"name": "BBC News", "url": "https://www.bbc.com/news", "description": "British Broadcasting Corporation"},
                {"name": "NPR", "url": "https://www.npr.org", "description": "National Public Radio"},
            ]
        }

# Global history storage (in-memory)
history = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/result")
def result():
    return render_template("result_enhanced.html")

@app.route("/history")
def history_page():
    return render_template("history.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    global history
    
    data = request.json
    url = data.get("url", "").strip()
    text = data.get("text", "").strip()
    
    if not url and not text:
        return jsonify({"error": "Please provide text or URL"}), 400
    
    # Scrape URL if provided
    if url:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            if len(text) > 5000:
                text = text[:5000]
        except Exception as e:
            return jsonify({"error": f"Failed to scrape URL: {str(e)}"}), 400
    
    # Clean text
    cleaned_text = ' '.join(text.split())[:5000]
    
    # Advanced classification with hybrid approach
    classification_result = advanced_classification(cleaned_text)
    
    # Get detailed explanation
    detailed_explanation = get_detailed_explanation(classification_result, cleaned_text)
    
    # Get related content
    is_fake = classification_result["verdict"] == "Likely Fake"
    related_content = get_related_content(cleaned_text, is_fake)
    
    # Build result
    result_data = {
        "inputText": cleaned_text[:200] + ("..." if len(cleaned_text) > 200 else ""),
        "fullText": cleaned_text,
        "score": classification_result["score"],
        "verdict": classification_result["verdict"],
        "confidence": classification_result["confidence"],
        "explanation": detailed_explanation,
        "fakeKeywords": classification_result["fake_keywords"],
        "reliableKeywords": classification_result["reliable_keywords"],
        "suspiciousPatterns": classification_result["suspicious_patterns"],
        "reliablePatterns": classification_result["reliable_patterns"],
        "mlScore": classification_result["ml_score"],
        "relatedContent": related_content,
        "modelStatus": model_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if classification_result["fact_check"]:
        result_data["factCheck"] = classification_result["fact_check"]
    
    # Add to history
    history.insert(0, {
        "text": cleaned_text[:100],
        "verdict": classification_result["verdict"],
        "score": classification_result["score"],
        "timestamp": result_data["timestamp"]
    })
    
    result_data["history"] = history[:20]  # Keep last 20
    
    return jsonify(result_data)

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify({"history": history[:20]})

if __name__ == "__main__":
    load_model()
    # Start browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=True, port=5000)
