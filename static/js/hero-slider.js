/* Home hero: auto-slides when there is more than one banner. Dots and swipe also work. */
(function () {
    var hero = document.getElementById('heroSlider');
    if (!hero) return;
    var slides = Array.prototype.slice.call(hero.querySelectorAll('.sj-hero-slide'));
    var dots = Array.prototype.slice.call(hero.querySelectorAll('.sj-hero-indicator span'));
    if (slides.length < 2) return;

    var current = 0, timer = null, DELAY = 5500;
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function show(n) {
        current = (n + slides.length) % slides.length;
        slides.forEach(function (s, i) { s.classList.toggle('is-active', i === current); });
        dots.forEach(function (d, i) { d.classList.toggle('active', i === current); });
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function start() {
        stop();
        if (reduce) return;
        timer = setInterval(function () { show(current + 1); }, DELAY);
    }

    dots.forEach(function (d, i) {
        d.addEventListener('click', function () { show(i); start(); });
    });

    // swipe on phones
    var x0 = null;
    hero.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    hero.addEventListener('touchend', function (e) {
        if (x0 === null) return;
        var dx = e.changedTouches[0].clientX - x0;
        x0 = null;
        if (Math.abs(dx) > 45) { show(current + (dx < 0 ? 1 : -1)); start(); }
    }, { passive: true });

    // do not slide while the tab is hidden
    document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });

    start();
})();
