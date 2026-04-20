document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("theme-toggle");
    const root = document.documentElement;
    const storageKey = "fakefilterTheme";

    const savedTheme = localStorage.getItem(storageKey);
    const defaultTheme = savedTheme || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    setTheme(defaultTheme);

    if (!toggle) {
        return;
    }

    toggle.addEventListener("click", () => {
        const current = root.getAttribute("data-theme") || "dark";
        const next = current === "dark" ? "light" : "dark";
        setTheme(next);
    });

    function setTheme(theme) {
        root.setAttribute("data-theme", theme);
        localStorage.setItem(storageKey, theme);
        toggle.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
    }
});