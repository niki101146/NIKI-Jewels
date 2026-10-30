document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("navbarSearchInput");
    const results = document.getElementById("searchProductResults");
    if (!input || !results) return;
    const form = input.form;
    let timer, pending, revision = 0;
    async function search(current) {
        const url = new URL(location.href);
        const query = input.value.trim();
        if (query) url.searchParams.set("q", query);
        else url.searchParams.delete("q");
        url.hash = "";
        pending = new AbortController();
        results.setAttribute("aria-busy", "true");
        try {
            const response = await fetch(url, {signal: pending.signal});
            if (!response.ok) throw new Error("Search unavailable");
            const html = new DOMParser().parseFromString(await response.text(), "text/html");
            const updated = html.getElementById("searchProductResults");
            if (current !== revision) return;
            if (!updated) throw new Error("Missing results");
            results.replaceChildren(...updated.childNodes);
            history.replaceState(null, "", url);
            const filters = document.getElementById("filterBox");
            if (filters) {
                let hidden = filters.querySelector('input[name="q"]');
                if (!hidden) {
                    hidden = document.createElement("input");
                    hidden.type = "hidden"; hidden.name = "q";
                    filters.append(hidden);
                }
                hidden.value = query;
            }
        } catch (error) {
            if (error.name !== "AbortError" && current === revision) location.assign(url);
        } finally {
            if (current === revision) results.removeAttribute("aria-busy");
        }
    }
    function schedule(immediate) {
        clearTimeout(timer);
        if (pending) pending.abort();
        const current = ++revision;
        timer = setTimeout(() => search(current), immediate ? 0 : 250);
    }
    input.addEventListener("input", () => schedule(false));
    form.addEventListener("submit", event => { event.preventDefault(); schedule(true); });
});
