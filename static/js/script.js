console.log("Luxora Jewellery website loaded");
console.log("Luxora Jewellery website loaded");

/* =========================================================
   MOBILE DRAWER MENU (Telegram style, slides from left)
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    var drawer   = document.getElementById("mainNavigation");
    var overlay  = document.getElementById("drawerOverlay");
    var openBtn  = document.getElementById("menuOpenBtn");
    var closeBtn = document.getElementById("menuCloseBtn");

    if (!drawer || !overlay || !openBtn) {
        return;
    }

    function openMenu() {
        drawer.classList.add("active");
        overlay.classList.add("active");
        document.body.classList.add("menu-open");
        openBtn.setAttribute("aria-expanded", "true");
    }

    function closeMenu() {
        drawer.classList.remove("active");
        overlay.classList.remove("active");
        document.body.classList.remove("menu-open");
        openBtn.setAttribute("aria-expanded", "false");
    }

    openBtn.addEventListener("click", openMenu);

    if (closeBtn) {
        closeBtn.addEventListener("click", closeMenu);
    }

    overlay.addEventListener("click", closeMenu);

    // Close when a menu link is tapped
    drawer.querySelectorAll(".navbar-link").forEach(function (link) {
        link.addEventListener("click", closeMenu);
    });

    // Close with Esc key
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closeMenu();
        }
    });

    // Close if the screen grows back to desktop size
    window.addEventListener("resize", function () {
        if (window.innerWidth > 991) {
            closeMenu();
        }
    });
});
/* =========================================================
   COLLECTIONS - MOBILE FILTER BUTTON (add at end of script.js)
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    var btn   = document.getElementById("filterToggleBtn");
    var box   = document.getElementById("filterBox");
    var badge = document.getElementById("filterCount");

    if (!btn || !box) {
        return;
    }

    // show how many filters are ticked on the Filter button
    function updateCount() {
        var n = box.querySelectorAll('input[type="checkbox"]:checked').length;

        if (badge) {
            badge.textContent = n;
            badge.hidden = (n === 0);
        }
    }

    // click Filter button -> show / hide the filter box
    btn.addEventListener("click", function () {
        var isOpen = box.classList.toggle("open");

        btn.classList.toggle("active", isOpen);
        btn.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    box.addEventListener("change", updateCount);

    updateCount();
});