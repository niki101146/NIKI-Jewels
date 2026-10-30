document.addEventListener("DOMContentLoaded", () => {
 const grid = document.getElementById("liveRates"), status = document.getElementById("rateStatus");
 if (!grid || !status) return;
 const money = new Intl.NumberFormat("en-IN", {style:"currency", currency:"INR"});
 const date = new Intl.DateTimeFormat("en-IN", {timeZone:"Asia/Kolkata", dateStyle:"medium", timeStyle:"short"});
 let busy = false, timer;
 async function update() {
  clearTimeout(timer);
  if (busy || document.hidden) return;
  busy = true;
  const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), 20000);
  try {
   const response = await fetch(grid.dataset.url, {cache:"no-store", signal:controller.signal});
   if (!response.ok) throw new Error();
   const data = await response.json();
   let fresh = 0;
   grid.querySelectorAll("[data-rate]").forEach(node => {
    const quote = data.quotes[node.dataset.rate];
    node.textContent = quote && quote.value != null ? money.format(quote.value) : "Unavailable";
    let note = node.nextElementSibling;
    if (!note || !note.classList.contains("quote-time")) {
     note = document.createElement("p"); note.className = "quote-time";
     note.style.cssText = "font-size:12px;line-height:1.5;color:#777;margin:10px 0";
     node.after(note);
    }
    note.textContent = quote && quote.quoted_at ? (quote.stale ? "Last known quote: " : "Quoted: ") + date.format(new Date(quote.quoted_at)) + " IST" : "Price feed unavailable; retrying automatically.";
    if (quote && !quote.stale) fresh++;
   });
   status.textContent = fresh === 4 ? "Automatic updates are on. Checks every minute." : "Some rates are unavailable or older quotes. Retrying automatically.";
  } catch (error) {
   status.textContent = "Cannot reach the price service. Displayed rates may be outdated; retrying automatically.";
  } finally {
   clearTimeout(timeout); busy = false;
   if (!document.hidden) timer = setTimeout(update, 60000);
  }
 }
 document.addEventListener("visibilitychange", () => { clearTimeout(timer); if (!document.hidden) update(); });
 window.addEventListener("online", update);
 update();
});
