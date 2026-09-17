/* ainative.ai — navigation, theme, evaluation form */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  // year
  var y = doc.getElementById("year"); if (y) y.textContent = new Date().getFullYear();
  // mobile menu
  var toggle = doc.querySelector(".menu-toggle"), nav = doc.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(open)); nav.setAttribute("data-open", String(open)); doc.body.setAttribute("data-menu-open", String(open));
    });
    doc.addEventListener("keydown", function (e) { if (e.key === "Escape" && nav.getAttribute("data-open") === "true") { toggle.click(); toggle.focus(); } });
    window.matchMedia("(min-width: 1024px)").addEventListener("change", function (m) { if (m.matches) { toggle.setAttribute("aria-expanded", "false"); nav.removeAttribute("data-open"); doc.body.removeAttribute("data-menu-open"); } });
  }
  // sub-menu (keyboard and touch)
  doc.querySelectorAll(".nav-sub-toggle").forEach(function (b) {
    var li = b.parentElement;
    b.addEventListener("click", function () { var open = b.getAttribute("aria-expanded") !== "true"; b.setAttribute("aria-expanded", String(open)); li.setAttribute("data-open", String(open)); });
    li.addEventListener("focusout", function (e) { if (!li.contains(e.relatedTarget)) { b.setAttribute("aria-expanded", "false"); li.removeAttribute("data-open"); } });
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
  // evaluation form
  doc.querySelectorAll(".eval-form").forEach(function (form) {
    var status = form.querySelector(".form-status"), endpoint = form.getAttribute("data-endpoint"), mailto = form.getAttribute("data-mailto");
    form.addEventListener("submit", function (e) {
      e.preventDefault(); status.className = "form-status"; status.textContent = "";
      var ok = true;
      form.querySelectorAll("[required]").forEach(function (f) { var bad = !f.value || (f.type === "email" && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.value)); f.setAttribute("aria-invalid", bad ? "true" : "false"); if (bad) ok = false; });
      if (!ok) { status.textContent = "A few fields need attention — the marked ones."; status.classList.add("is-error"); return; }
      if (form.querySelector(".hp") && form.querySelector(".hp").value) { status.textContent = "Thank you."; return; }
      var data = new FormData(form);
      if (endpoint) {
        var btn = form.querySelector("button[type=submit]"); btn.disabled = true; btn.textContent = "Sending…";
        fetch(endpoint, { method: "POST", body: data, headers: { "Accept": "application/json" } }).then(function (r) {
          if (!r.ok) throw new Error("send failed");
          form.reset(); btn.disabled = false; btn.textContent = "Book the Evaluation";
          status.textContent = "Received. A person will reply to set the time — thank you.";
        }).catch(function () {
          btn.disabled = false; btn.textContent = "Book the Evaluation";
          status.textContent = "That did not send. Please try again" + (mailto ? ", or email " + mailto : "") + "."; status.classList.add("is-error");
        });
      } else if (mailto) {
        var lines = []; data.forEach(function (v, k) { if (k.charAt(0) !== "_" && v) lines.push(k + ": " + v); });
        window.location.href = "mailto:" + mailto + "?subject=" + encodeURIComponent("Evaluation request") + "&body=" + encodeURIComponent(lines.join("\n"));
        status.textContent = "Your email app should open with the request. If it did not, email us directly.";
      } else {
        status.textContent = "The form is not connected yet. Set FORM_ENDPOINT or CONTACT_EMAIL in the site configuration."; status.classList.add("is-error");
      }
    });
  });
})();
