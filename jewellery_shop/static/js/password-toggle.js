/* Adds a show/hide (eye) button to every <input type="password">. */
(function () {
    var css = ".pw-wrap{position:relative;display:block;width:100%}" +
        ".pw-wrap>input{padding-right:46px !important}" +
        ".pw-eye{position:absolute;top:0;right:0;height:100%;min-height:42px;width:46px;display:flex;align-items:center;justify-content:center;" +
        "padding:0;margin:0;border:0;background:transparent;color:var(--zy-gold-text,#c9a24d);font-size:19px;line-height:1;cursor:pointer}" +
        ".pw-eye:hover{color:var(--zy-gold,#c9a24d)}.pw-eye:focus-visible{outline:2px solid var(--zy-gold,#c9a24d);outline-offset:-4px;border-radius:8px}";
    var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

    function attach(input) {
        if (input.dataset.pwEye) return;
        input.dataset.pwEye = "1";
        var wrap = document.createElement("span"); wrap.className = "pw-wrap";
        input.parentNode.insertBefore(wrap, input); wrap.appendChild(input);
        var btn = document.createElement("button");
        btn.type = "button"; btn.className = "pw-eye";
        btn.setAttribute("aria-label", "Show password"); btn.setAttribute("aria-pressed", "false");
        btn.innerHTML = '<i class="bi bi-eye" aria-hidden="true"></i>';
        btn.addEventListener("click", function () {
            var show = input.type === "password";
            input.type = show ? "text" : "password";
            btn.innerHTML = '<i class="bi ' + (show ? "bi-eye-slash" : "bi-eye") + '" aria-hidden="true"></i>';
            btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
            btn.setAttribute("aria-pressed", show ? "true" : "false");
            input.focus();
        });
        wrap.appendChild(btn);
    }
    function init() { Array.prototype.forEach.call(document.querySelectorAll('input[type="password"]'), attach); }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
