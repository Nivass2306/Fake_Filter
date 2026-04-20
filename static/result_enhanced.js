// Enhanced Result Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const hasResult = localStorage.getItem('analysisResult');

    if (hasResult) {
        const result = JSON.parse(hasResult);
        displayResult(result);
        localStorage.removeItem('analysisResult');
    }
});

function displayResult(result) {
    // Determine score class for color coding
    const scoreValue = result.score;
    let scoreClass = 'uncertain';
    if (scoreValue >= 70) {
        scoreClass = 'fake'; // Red
    } else if (scoreValue <= 30) {
        scoreClass = 'real'; // Green
    }

    // Update verdict card
    const scoreCircle = document.getElementById('score-visual');
    scoreCircle.classList.add(scoreClass);
    document.getElementById('score-number').textContent = result.score;

    const verdictText = result.verdict;
    const verdictEmoji = scoreValue >= 70 ? '🚨' : scoreValue <= 30 ? '✓' : '❓';
    document.getElementById('verdict-text').textContent = `${verdictEmoji} ${verdictText}`;
    document.getElementById('confidence-text').textContent = `Confidence: ${result.confidence}%`;

    // Input summary
    document.getElementById('input-text').textContent = result.inputText;

    // Explanation
    document.getElementById('explanation').innerHTML = result.explanation;

    // Score breakdown
    if (result.mlScore !== null) {
        document.getElementById('ml-progress').style.width = result.mlScore + '%';
        document.getElementById('ml-score').textContent = result.mlScore + '%';
    } else {
        document.querySelector('.score-item:nth-child(1)').style.opacity = '0.5';
        document.getElementById('ml-score').textContent = 'No ML model';
    }

    document.getElementById('fake-probability').textContent = result.fakeProbability !== undefined ? result.fakeProbability : '--';
    document.getElementById('real-probability').textContent = result.realProbability !== undefined ? result.realProbability : '--';

    document.getElementById('keyword-progress').style.width = result.keywordScore + '%';
    document.getElementById('keyword-score').textContent = result.keywordScore + '%';

    document.getElementById('pattern-progress').style.width = result.patternScore + '%';
    document.getElementById('pattern-score').textContent = result.patternScore + '%';

    // Keywords
    const fakeKeywordsContainer = document.getElementById('fake-keywords');
    if (result.fakeKeywords && result.fakeKeywords.length > 0) {
        fakeKeywordsContainer.innerHTML = result.fakeKeywords
            .map(kw => `<span class="tag tag-fake">${escapeHtml(kw)}</span>`)
            .join('');
    } else {
        fakeKeywordsContainer.innerHTML = '<span class="tag tag-fake">None detected</span>';
    }

    const reliableKeywordsContainer = document.getElementById('reliable-keywords');
    if (result.reliableKeywords && result.reliableKeywords.length > 0) {
        reliableKeywordsContainer.innerHTML = result.reliableKeywords
            .map(kw => `<span class="tag tag-reliable">${escapeHtml(kw)}</span>`)
            .join('');
    } else {
        reliableKeywordsContainer.innerHTML = '<span class="tag tag-reliable">None detected</span>';
    }

    // Language Patterns
    const suspiciousPatterns = document.getElementById('suspicious-patterns');
    if (result.suspiciousPatterns && result.suspiciousPatterns.length > 0) {
        suspiciousPatterns.innerHTML = result.suspiciousPatterns
            .map(p => `<li>🚩 ${escapeHtml(p)}</li>`)
            .join('');
    } else {
        suspiciousPatterns.innerHTML = '<li>No suspicious patterns detected</li>';
    }

    const reliablePatterns = document.getElementById('reliable-patterns');
    if (result.reliablePatterns && result.reliablePatterns.length > 0) {
        reliablePatterns.innerHTML = result.reliablePatterns
            .map(p => `<li>✓ ${escapeHtml(p)}</li>`)
            .join('');
    } else {
        reliablePatterns.innerHTML = '<li>No reliable patterns detected</li>';
    }

    // Fact check display
    if (result.factCheck) {
        document.getElementById('fact-check-section').style.display = 'block';
        document.getElementById('fact-check-explanation').textContent = result.factCheck.explanation;
        document.getElementById('fact-check-source').textContent = result.factCheck.source;
        const link = document.getElementById('fact-check-link');
        link.href = result.factCheck.link;
        link.textContent = '📚 Learn More';
    }

    // Related resources
    if (result.relatedContent) {
        const resourcesContainer = document.getElementById('resources-container');
        const resourcesTitle = document.getElementById('resources-title');
        resourcesTitle.textContent = result.relatedContent.title;

        resourcesContainer.innerHTML = result.relatedContent.resources
            .map(resource => `
                <div class="resource-item">
                    <h4>${escapeHtml(resource.name)}</h4>
                    <p>${escapeHtml(resource.description)}</p>
                    <a href="${resource.url}" target="_blank" class="resource-link">Visit →</a>
                </div>
            `)
            .join('');
    }

    // Model status
    document.getElementById('model-status').textContent = `Model Status: ${result.modelStatus}`;

    // Setup buttons
    setupButtons(result);
}

function setupButtons(result) {
    // Search on Google
    document.getElementById('search-google').addEventListener('click', function() {
        const query = encodeURIComponent(result.inputText);
        window.open(`https://www.google.com/search?q=${query}`, '_blank');
    });

    // Check on Snopes
    document.getElementById('check-snopes').addEventListener('click', function() {
        const query = encodeURIComponent(result.inputText);
        window.open(`https://www.snopes.com/?s=${query}`, '_blank');
    });

    // Back to home
    document.getElementById('back-button').addEventListener('click', function() {
        window.location.href = '/';
    });
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
