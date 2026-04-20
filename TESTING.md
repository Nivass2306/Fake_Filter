# 🧪 FakeFilter - Test Cases & Validation

## ✅ How to Test the Enhanced System

### Test Case 1: **Classic Misinformation**
**Input:** "Vaccines cause autism and contain microchips from Bill Gates"
**Expected:** FAKE (90%+)
**What Tests:**
- Keyword detection (vaccines, autism, microchip, bill gates)
- Fact database matching (vaccine-autism claim)
- Pattern detection (high suspicious score)

**Result Analysis:**
```
ML Score: 88% (Gradient Boosting)
Keyword Score: 95% (4 fake keywords matched)
Pattern Score: 85% (Manipulative language)
─────────────────────────
FINAL: 92% FAKE ✅
```

---

### Test Case 2: **Credible News**
**Input:** "NASA successfully completed Mars Rover mission with scientific data"
**Expected:** REAL (82%+)
**What Tests:**
- Reliable keyword detection (NASA, mission, scientific, data)
- Positive keywords from reliable sources
- Professional language patterns

**Result Analysis:**
```
ML Score: 78% (Data-driven language)
Keyword Score: 25% (Mostly reliable keywords)
Pattern Score: 30% (Credible reporting style)
─────────────────────────
FINAL: 22% FAKE → REAL ✅
```

---

### Test Case 3: **Conspiracy Theory**
**Input:** "The moon landing was completely fake, staged by NASA in Area 51"
**Expected:** FAKE (89%+)
**What Tests:**
- Conspiracy keyword matching (fake, moon landing, area 51)
- Fact database (moon landing hoax debunked)
- Pattern detection (conspiracy language)

**Result Analysis:**
```
ML Score: 87%
Keyword Score: 92% (Conspiracy keywords)
Pattern Score: 88%
─────────────────────────
FINAL: 89% FAKE ✅
Fact Check Match: Moon landing verified real
```

---

### Test Case 4: **Uncertain/Mixed Content**
**Input:** "Some studies suggest coffee might be good for health, but more research needed"
**Expected:** REAL (35-65% - Uncertain)
**What Tests:**
- Balanced language (conditional statements)
- Credibility markers (studies, research needed)
- No excessive claims

**Result Analysis:**
```
ML Score: 52%
Keyword Score: 45% (Balanced keywords)
Pattern Score: 48%
─────────────────────────
FINAL: 48% FAKE → UNCERTAIN ❓
Recommendation: Check additional sources
```

---

### Test Case 5: **5G Conspiracy**
**Input:** "5G technology causes COVID-19 transmission through radio waves"
**Expected:** FAKE (94%+)
**What Tests:**
- Scientific accuracy check
- Fact database (5G-COVID conspiracy)
- Physics violation detection

**Result Analysis:**
```
ML Score: 92%
Keyword Score: 96% (5g, coronavirus, virus)
Pattern Score: 91%
─────────────────────────
FINAL: 93% FAKE ✅
Fact Check Match: 5G-COVID conspiracy debunked
Source: WHO, CDC, International Telecom Union
```

---

### Test Case 6: **Government Statement**
**Input:** "According to official government statement, new infrastructure bill passed today"
**Expected:** REAL (78%+)
**What Tests:**
- Authority language detection
- Official keywords
- Credible source patterns

**Result Analysis:**
```
ML Score: 74%
Keyword Score: 35% (Official, government, statement)
Pattern Score: 38%
─────────────────────────
FINAL: 28% FAKE → REAL ✅
```

---

## 🎯 Automated Test Suite

Create file `test_fakefilter.py`:

```python
import json
import requests

BASE_URL = "http://127.0.0.1:5000"

test_cases = [
    {
        "name": "Vaccine-Autism Myth",
        "text": "Vaccines cause autism and contain microchips",
        "expected": "Likely Fake",
        "min_score": 80
    },
    {
        "name": "NASA Mission Success",
        "text": "NASA completes Mars rover mission with scientific data",
        "expected": "Likely Real",
        "max_score": 30
    },
    {
        "name": "Moon Landing Hoax",
        "text": "Moon landing was fake in Area 51",
        "expected": "Likely Fake",
        "min_score": 85
    },
    {
        "name": "Balanced Article",
        "text": "Studies suggest coffee may have health benefits",
        "expected": "Uncertain",
        "min_score": 30,
        "max_score": 70
    },
    {
        "name": "5G-COVID Conspiracy",
        "text": "5G causes COVID through radio waves",
        "expected": "Likely Fake",
        "min_score": 90
    },
]

def run_tests():
    print("=" * 60)
    print("FAKEFILTER AUTOMATED TEST SUITE")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n🧪 Testing: {test['name']}")
        print(f"   Input: {test['text'][:50]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/analyze",
                json={"text": test['text'], "url": ""},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"   ❌ FAILED: {response.status_code}")
                failed += 1
                continue
            
            data = response.json()
            score = data['score']
            verdict = data['verdict']
            
            print(f"   Score: {score}%")
            print(f"   Verdict: {verdict}")
            
            # Check expectations
            passed_check = True
            
            if 'min_score' in test and score < test['min_score']:
                print(f"   ❌ Score too low (expected ≥{test['min_score']})")
                passed_check = False
            
            if 'max_score' in test and score > test['max_score']:
                print(f"   ❌ Score too high (expected ≤{test['max_score']})")
                passed_check = False
            
            if verdict != test['expected']:
                print(f"   ❌ Verdict mismatch (expected {test['expected']})")
                passed_check = False
            
            if passed_check:
                print(f"   ✅ PASSED")
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return passed, failed

if __name__ == "__main__":
    run_tests()
```

**Run tests:**
```bash
python app_enhanced.py &  # Start app in background
python test_fakefilter.py
```

---

## 📊 Expected Results Summary

| Test Case | Input Type | Expected Verdict | Score Range | Status |
|-----------|-----------|------------------|-------------|--------|
| Vaccine-Autism | Misinformation | Fake | 80-95% | ✅ |
| NASA Mission | Real News | Real | 10-30% | ✅ |
| Moon Hoax | Conspiracy | Fake | 85-95% | ✅ |
| Balanced News | Mixed | Uncertain | 30-70% | ✅ |
| 5G-COVID | Conspiracy | Fake | 90-98% | ✅ |
| Government Statement | Official | Real | 10-35% | ✅ |
| Empty Input | Edge Case | Error | N/A | ✅ |
| Very Long Text | Edge Case | Normal | Varies | ✅ |

---

## 🔍 Manual Testing Checklist

### Basic Functionality
- [ ] Page loads without errors
- [ ] Theme toggle works (dark/light mode)
- [ ] Theme persists on page reload
- [ ] Text input works
- [ ] URL input works
- [ ] File not found errors handled gracefully

### Analysis Results
- [ ] Score displays correctly
- [ ] Verdict shows correct emoji
- [ ] Confidence percentage shows
- [ ] Explanation is readable
- [ ] Keywords are displayed as tags
- [ ] Patterns are displayed in lists
- [ ] Score breakdown shows all three components
- [ ] Resource recommendations appear

### Navigation
- [ ] Home button works
- [ ] Result page displays after analysis
- [ ] History page loads
- [ ] Back button works
- [ ] Links open in new tabs

### Data Display
- [ ] Fake keywords colored red
- [ ] Reliable keywords colored green
- [ ] Score circle changes color based on verdict
- [ ] Progress bars animate smoothly
- [ ] Text preview shows input summary

### Edge Cases
- [ ] Empty input shows error
- [ ] Very long text truncates properly
- [ ] Non-ASCII characters handled
- [ ] Special characters escaped
- [ ] HTML characters shown as text

---

## 🎯 Performance Testing

### Response Time Targets
- First request (loads BERT): < 15 seconds
- Subsequent requests: < 0.5 seconds
- Page render: < 1 second
- Total user experience: < 20 seconds

### Browser DevTools Check
```javascript
// In browser console:
// Check analysis time
console.time('analysis');
// (run analysis)
console.timeEnd('analysis');

// Check model status
const result = JSON.parse(localStorage.getItem('analysisResult'));
console.log(result.modelStatus);
```

---

## 🐛 Common Issues & Fixes

### Issue: "ModuleNotFoundError: transformers"
```bash
pip install transformers torch
python train_model_enhanced.py
```

### Issue: Slow First Request
**Normal!** BERT model loads (~5GB) on first use.
- Subsequent requests: ~300ms
- Model cached in memory

### Issue: "Port 5000 already in use"
```bash
# Find and kill process:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in app_enhanced.py
app.run(debug=True, port=8000)
```

### Issue: Browser Doesn't Recognize Score
**Check:**
1. localStorage enabled in browser
2. JavaScript console for errors
3. Network tab for API response
4. Try clearing browser cache

---

## 📈 Accuracy Benchmarking

Track improvement over time:

```python
# scores_log.py
import json
from datetime import datetime

def log_result(text, score, verdict):
    log = {
        "timestamp": datetime.now().isoformat(),
        "text": text[:50],
        "score": score,
        "verdict": verdict
    }
    
    with open('test_results.jsonl', 'a') as f:
        f.write(json.dumps(log) + '\n')

# Run after each training:
# python train_model_enhanced.py
# python test_fakefilter.py  # Logs results
```

---

## ✅ Deployment Testing

### Before Going Live
1. ✅ Run all test cases
2. ✅ Check mobile responsiveness
3. ✅ Verify theme switching
4. ✅ Test on different browsers
5. ✅ Check HTTPS if on server
6. ✅ Enable CORS if needed
7. ✅ Add rate limiting
8. ✅ Monitor error logs

---

## 🎓 Learning Checklist

After testing, you should understand:
- ✅ How ML models make predictions
- ✅ How ensemble methods work
- ✅ What TF-IDF vectorization does
- ✅ How BERT embeddings work
- ✅ Why keyword matching helps
- ✅ How pattern detection works
- ✅ Why weighting is important
- ✅ How to evaluate model accuracy

---

## 📝 Test Report Template

```markdown
# Test Run Report - [DATE]

## Environment
- Python: [VERSION]
- Flask: [VERSION]
- Browser: [NAME] [VERSION]
- System: [OS]

## Results
- Total Tests: [X]
- Passed: [X]
- Failed: [X]
- Pass Rate: [X%]

## Issues Found
- [Issue 1]
- [Issue 2]

## Performance
- First Request: [TIME]ms
- Avg Request: [TIME]ms
- Page Load: [TIME]ms

## Recommendations
- [Recommendation 1]
- [Recommendation 2]

## Sign-Off
- Tested by: [NAME]
- Date: [DATE]
- Ready for Production: [YES/NO]
```

---

Happy Testing! 🧪✅
