document.addEventListener("DOMContentLoaded", () => {
    const rawData = localStorage.getItem("latestResult") || localStorage.getItem("analysisResult");
    const data = rawData ? JSON.parse(rawData) : null;
    if (!data) {
        window.location.href = "/";
        return;
    }

    document.getElementById("input-text").textContent = data.inputText;
    document.getElementById("verdict").textContent = data.verdict;
    document.getElementById("score").textContent = data.score;
    document.getElementById("explanation").textContent = data.explanation;
    document.getElementById("fake-count").textContent = data.fakeCount;
    document.getElementById("source").textContent = data.source === "ml" ? "Model prediction" : "Rule-based fallback";

    const fakeDetails = document.getElementById("fake-details");
    const realDetails = document.getElementById("real-details");
    const whyFakeEl = document.getElementById("why-fake");
    const correctNewsEl = document.getElementById("correct-news");
    const moreDetailsEl = document.getElementById("more-details");
    const openLinkBtn = document.getElementById("open-link");
    const openLinkRealBtn = document.getElementById("open-link-real");

    if (data.verdict === "Likely Fake") {
        whyFakeEl.textContent = data.whyFake || "No specific reason available.";
        correctNewsEl.textContent = data.correctNews || "No correction available.";
        fakeDetails.style.display = "block";
        realDetails.style.display = "none";
        if (data.link) {
            openLinkBtn.style.display = "inline-block";
            openLinkBtn.onclick = () => window.open(data.link, '_blank');
        } else {
            openLinkBtn.style.display = "none";
        }
        document.getElementById("search-more-fake").onclick = () => {
            const query = encodeURIComponent(data.inputText.substring(0, 100));
            window.open(`https://www.google.com/search?q=${query}`, '_blank');
        };
    } else {
        moreDetailsEl.textContent = data.moreDetails || "No additional details available.";
        realDetails.style.display = "block";
        fakeDetails.style.display = "none";
        if (data.link) {
            openLinkRealBtn.style.display = "inline-block";
            openLinkRealBtn.onclick = () => window.open(data.link, '_blank');
        } else {
            openLinkRealBtn.style.display = "none";
        }
        document.getElementById("search-more-real").onclick = () => {
            const query = encodeURIComponent(data.inputText.substring(0, 100));
            window.open(`https://www.google.com/search?q=${query}`, '_blank');
        };
    }
});