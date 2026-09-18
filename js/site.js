/* ainative.ai — navigation, theme, evaluation form */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  // year
  var y = doc.getElementById("year"); if (y) y.textContent = new Date().getFullYear();
  // mobile menu
  var toggle = doc.querySelector(".menu-toggle"), nav = doc.getElementById("site-nav"), savedY = 0;
  function setMenu(open) {
    toggle.setAttribute("aria-expanded", String(open));
    if (open) { savedY = window.scrollY || 0; nav.setAttribute("data-open", "true"); root.setAttribute("data-menu-open", "true"); }
    else { nav.removeAttribute("data-open"); root.removeAttribute("data-menu-open"); window.scrollTo(0, savedY); }
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function (e) { e.preventDefault(); setMenu(toggle.getAttribute("aria-expanded") !== "true"); });
    nav.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", function () { if (root.getAttribute("data-menu-open") === "true") setMenu(false); }); });
    doc.addEventListener("keydown", function (e) { if (e.key === "Escape" && root.getAttribute("data-menu-open") === "true") { setMenu(false); toggle.focus(); } });
    var mq = window.matchMedia("(min-width: 1024px)"); var onChange = function (m) { if (m.matches && root.getAttribute("data-menu-open") === "true") setMenu(false); };
    if (mq.addEventListener) mq.addEventListener("change", onChange); else if (mq.addListener) mq.addListener(onChange);
  }
  // sub-menu (keyboard and touch)
  doc.querySelectorAll(".nav-sub-toggle").forEach(function (b) {
    var li = b.parentElement;
    b.addEventListener("click", function () { var open = b.getAttribute("aria-expanded") !== "true"; b.setAttribute("aria-expanded", String(open)); li.setAttribute("data-open", String(open)); });
    li.addEventListener("focusout", function (e) { if (!li.contains(e.relatedTarget)) { b.setAttribute("aria-expanded", "false"); li.removeAttribute("data-open"); } });
    li.addEventListener("mouseleave", function () { b.setAttribute("aria-expanded", "false"); li.removeAttribute("data-open"); });
    li.addEventListener("mouseenter", function () { b.setAttribute("aria-expanded", "true"); li.setAttribute("data-open", "true"); });
  });
  // theme: auto → light → dark
  var tb = doc.getElementById("theme-toggle"), tl = doc.getElementById("theme-label");
  function label(t) { return t === "light" ? "Light" : t === "dark" ? "Dark" : "Auto"; }
  var cur = root.getAttribute("data-theme") || "auto"; if (tl) tl.textContent = label(cur);
  if (tb) tb.addEventListener("click", function () {
    cur = cur === "auto" ? "light" : cur === "light" ? "dark" : "auto";
    if (cur === "auto") { root.setAttribute("data-theme", "auto"); try { localStorage.removeItem("an-theme"); } catch (e) {} }
    else { root.setAttribute("data-theme", cur); try { localStorage.setItem("an-theme", cur); } catch (e) {} }
    if (tl) tl.textContent = label(cur);
  });
  // evaluation form — delivered as an email (Web3Forms) using js/config.js; falls back to the visitor's email app
  var cfg = window.AI_NATIVE_SITE || {};
  doc.querySelectorAll(".eval-form").forEach(function (form) {
    var status = form.querySelector(".form-status");
    form.addEventListener("submit", function (e) {
      e.preventDefault(); status.className = "form-status"; status.textContent = "";
      var ok = true;
      form.querySelectorAll("[required]").forEach(function (f) { var bad = !f.value || (f.type === "email" && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.value)); f.setAttribute("aria-invalid", bad ? "true" : "false"); if (bad) ok = false; });
      if (!ok) { status.textContent = "A few fields need attention — the marked ones."; status.classList.add("is-error"); return; }
      var hp = form.querySelector("input[name=_gotcha]"), bc = form.querySelector("input[name=botcheck]");
      if ((hp && hp.value) || (bc && bc.checked)) { status.textContent = "Thank you."; return; }
      var data = new FormData(form); data.delete("botcheck"); data.delete("_gotcha");
      var btn = form.querySelector("button[type=submit]");
      if (cfg.formEndpoint && cfg.formAccessKey) {
        data.append("access_key", cfg.formAccessKey);
        btn.disabled = true; btn.textContent = "Sending…";
        fetch(cfg.formEndpoint, { method: "POST", body: data, headers: { Accept: "application/json" } }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok && j && j.success !== false, j: j }; }); }).then(function (res) {
          btn.disabled = false; btn.textContent = "Book the Evaluation";
          if (!res.ok) throw new Error("send failed");
          form.reset(); status.textContent = "Received. A person will reply to set the time — thank you.";
        }).catch(function () {
          btn.disabled = false; btn.textContent = "Book the Evaluation";
          status.textContent = "That did not send. Please try again" + (cfg.formEmail ? ", or email " + cfg.formEmail : "") + "."; status.classList.add("is-error");
        });
      } else if (cfg.formEmail) {
        var lines = []; data.forEach(function (v, k) { if (k !== "subject" && k !== "from_name" && v) lines.push(k + ": " + v); });
        window.location.href = "mailto:" + cfg.formEmail + "?subject=" + encodeURIComponent("Evaluation request from ainative.ai") + "&body=" + encodeURIComponent(lines.join("\n"));
        status.textContent = "Your email app should open with the request. If it did not, email " + cfg.formEmail + ".";
      } else {
        status.textContent = "The form is not connected yet."; status.classList.add("is-error");
      }
    });
  });
})();
