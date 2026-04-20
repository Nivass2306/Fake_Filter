document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch("/get_history");
    const history = await response.json();

    const historyList = document.getElementById("history-list");
    if (!history || !history.length) {
        historyList.innerHTML = "<li>No history available.</li>";
        return;
    }

    historyList.innerHTML = history
        .map((entry) => {
            return `
                <li>
                    <div class="history-entry-title">
                        <span>${entry.verdict}</span>
                        <span>${entry.score}%</span>
                    </div>
                    <div class="history-entry-time">${new Date(entry.timestamp).toLocaleString()}</div>
                    <div>${entry.text}</div>
                </li>
            `;
        })
        .join("");

    document.getElementById("clear-history").addEventListener("click", async () => {
        await fetch("/clear_history", { method: "POST" });
        historyList.innerHTML = "<li>History cleared.</li>";
    });
});