document.addEventListener("DOMContentLoaded", () => {
    const analyzeButton = document.getElementById("analyze-button");
    const statusMessage = document.getElementById("status-message");

    analyzeButton.addEventListener("click", async () => {
        const text = document.getElementById("news-text").value.trim();
        const url = document.getElementById("news-url").value.trim();

        if (!text && !url) {
            alert("Please enter news text or a URL to analyze.");
            return;
        }

        statusMessage.textContent = "Analyzing...";
        statusMessage.style.color = "blue";

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text, url }),
            });

            const data = await response.json();
            if (!response.ok) {
                alert(data.error || "Analysis failed.");
                statusMessage.textContent = "Analysis failed.";
                statusMessage.style.color = "red";
                return;
            }

            // Store result in localStorage and redirect to result page
            const jsonData = JSON.stringify(data);
            localStorage.setItem("analysisResult", jsonData);
            localStorage.setItem("latestResult", jsonData);
            // Give localStorage time to persist
            setTimeout(() => {
                window.location.href = "/result";
            }, 100);
        } catch (error) {
            alert("Network error: " + error.message);
            statusMessage.textContent = "Network error.";
            statusMessage.style.color = "red";
        }
    });
});
