/* NIKI Jewels - light / dark mode toggle.
   The saved choice is applied before first paint by a tiny inline script in <head>. */
(function () {
    var KEY = "niki-theme";
    var root = document.documentElement;

    function saved() {
        try { return localStorage.getItem(KEY); } catch (e) { return null; }
    }

    function current() {
        return root.getAttribute("data-bs-theme") === "light" ? "light" : "dark";
    }

    function refresh() {
        var isLight = current() === "light";
        var label = isLight ? "Switch to dark mode" : "Switch to light mode";
        document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
            btn.setAttribute("aria-label", label);
            btn.setAttribute("title", label);
            btn.setAttribute("aria-pressed", isLight ? "true" : "false");
        });
    }

    function apply(theme) {
        root.classList.add("theme-animating");
        root.setAttribute("data-bs-theme", theme);
        try { localStorage.setItem(KEY, theme); } catch (e) {}
        refresh();
        window.setTimeout(function () { root.classList.remove("theme-animating"); }, 320);
    }

    document.addEventListener("DOMContentLoaded", function () {
        refresh();
        document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                apply(current() === "light" ? "dark" : "light");
            });
        });
    });

    // keep several open tabs in sync
    window.addEventListener("storage", function (e) {
        if (e.key === KEY && (e.newValue === "light" || e.newValue === "dark")) {
            root.setAttribute("data-bs-theme", e.newValue);
            refresh();
        }
    });
})();
