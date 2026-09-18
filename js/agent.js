/* ainative.ai — the AI Native service agent (front end)
   Modes: "demo" — a scripted responder built from the site's own answers so the experience can be reviewed before the backend exists.
          "live" — POSTs each message to AGENT.config.endpoint and renders the messages it returns (see README-AGENT.md for the contract). */
(function () {
  "use strict";
  var doc = document;
  var CFG = window.AI_NATIVE_SITE || {};
  var AGENT = window.AINativeAgent = {
    config: { mode: CFG.agentMode || "demo", endpoint: CFG.agentEndpoint || "", phone: CFG.phone || "", email: CFG.email || "", calendar: CFG.calendar || "", formEndpoint: CFG.formEndpoint || "", formAccessKey: CFG.formAccessKey || "", formEmail: CFG.formEmail || "" },
    open: open, close: close, send: send, mount: mount
  };
  var BADGE = '<svg viewBox="0 0 100 115" aria-hidden="true"><path d="M17,0 H83 A17,17 0 0 1 100,17 V80.5 H0 V17 A17,17 0 0 1 17,0 Z M29,14.1 H71 A4.3,4.3 0 0 1 71,22.7 H29 A4.3,4.3 0 0 1 29,14.1 Z" fill="currentColor" fill-rule="evenodd"/><path d="M0,80.5 H100 V98 A17,17 0 0 1 83,115 H17 A17,17 0 0 1 0,98 Z" fill="#E8A33D"/></svg>';
  var GREETING = [{ type: "text", text: "Hi — I'm the AI Native service agent. I'm an AI agent, powered by AI Native: the same agent we install for clients. What can I help with?" },
                  { type: "chips", options: ["What does the Evaluation cost?", "How does an agent hand off to a person?", "What would you install at an HVAC company?", "Book the Evaluation"] }];
  var KEY = "an-agent-history", SID = "an-agent-session";
  var history = load(); var els = {}; var inlineHost = null; var busy = false;

  function load() { try { return JSON.parse(sessionStorage.getItem(KEY) || "[]"); } catch (e) { return []; } }
  function save() { try { sessionStorage.setItem(KEY, JSON.stringify(history.slice(-60))); } catch (e) {} }
  function sessionId() { try { var s = sessionStorage.getItem(SID); if (!s) { s = "s" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8); sessionStorage.setItem(SID, s); } return s; } catch (e) { return "s0"; } }
  function h(tag, cls, html) { var e = doc.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // ---------- UI ----------
  function build(host, inline) {
    var panel = h("section", "agent-panel" + (inline ? " is-inline" : ""), "");
    panel.setAttribute("role", inline ? "region" : "dialog"); panel.setAttribute("aria-label", "AI Native service agent");
    if (!inline) panel.setAttribute("aria-modal", "false");
    panel.innerHTML =
      '<header class="agent-head"><span class="agent-avatar">' + BADGE + '</span><div class="agent-id"><strong>AI Native service agent</strong><span>AI agent · replies in seconds</span></div>' +
      '<div class="agent-head-actions"><button type="button" class="agent-reset" title="Start over">Start over</button>' + (inline ? "" : '<button type="button" class="agent-close" aria-label="Close">×</button>') + '</div></header>' +
      '<div class="agent-log" aria-live="polite" aria-relevant="additions"></div>' +
      '<form class="agent-composer"><label class="sr" for="' + (inline ? "agent-inline-input" : "agent-input") + '">Message</label><textarea id="' + (inline ? "agent-inline-input" : "agent-input") + '" rows="1" placeholder="Ask a question…" autocomplete="off"></textarea><button type="submit" class="agent-send" aria-label="Send"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h14M12 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></button></form>' +
      '<p class="agent-foot">This is the same agent we install. Want a person? Type <b>person</b>.</p>';
    host.appendChild(panel);
    var log = panel.querySelector(".agent-log"), form = panel.querySelector(".agent-composer"), ta = panel.querySelector("textarea");
    form.addEventListener("submit", function (e) { e.preventDefault(); var t = ta.value.trim(); if (!t) return; ta.value = ""; ta.style.height = ""; send(t); });
    ta.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });
    ta.addEventListener("input", function () { ta.style.height = "auto"; ta.style.height = Math.min(ta.scrollHeight, 120) + "px"; });
    panel.querySelector(".agent-reset").addEventListener("click", function () { history = []; save(); renderAll(); reply(GREETING); });
    if (!inline) panel.querySelector(".agent-close").addEventListener("click", close);
    return { panel: panel, log: log, ta: ta };
  }

  function addMsg(msg, who) {
    // renders into every mounted log (floating panel + inline showcase share one conversation)
    each(function (ui) {
      var row = h("div", "agent-msg " + (who === "user" ? "is-user" : "is-agent"));
      if (msg.type === "text") row.appendChild(h("div", "agent-bubble", esc(msg.text).replace(/\n/g, "<br>")));
      else if (msg.type === "chips") {
        var wrap = h("div", "agent-chips"); msg.options.forEach(function (o) { var b = h("button", "agent-chip", esc(o)); b.type = "button"; b.addEventListener("click", function () { send(o); }); wrap.appendChild(b); }); row.appendChild(wrap);
      } else if (msg.type === "card") row.appendChild(card(msg));
      ui.log.appendChild(row); ui.log.scrollTop = ui.log.scrollHeight;
    });
  }
  function card(m) {
    var c = h("div", "agent-card");
    if (m.kind === "link") c.innerHTML = '<strong>' + esc(m.title) + '</strong><p>' + esc(m.text || "") + '</p><a class="btn btn-secondary btn-sm" href="' + esc(m.href) + '">' + esc(m.cta || "Open") + '</a>';
    else if (m.kind === "handoff") {
      var a = AGENT.config, parts = [];
      if (a.phone) parts.push('<a class="btn btn-secondary btn-sm" href="tel:' + esc(a.phone.replace(/[^\d+]/g, "")) + '">Call ' + esc(a.phone) + '</a>');
      if (a.calendar) parts.push('<a class="btn btn-secondary btn-sm" href="' + esc(a.calendar) + '" target="_blank" rel="noopener">Pick a time now</a>');
      if (a.email) parts.push('<a class="btn btn-secondary btn-sm" href="mailto:' + esc(a.email) + '">Email ' + esc(a.email) + '</a>');
      c.innerHTML = '<strong>' + esc(m.title || "A person, not the agent") + '</strong><p>' + esc(m.text || "Here are the ways to reach a person. I've stepped back.") + '</p><div class="agent-card-actions">' + parts.join("") + '</div>';
    } else if (m.kind === "book") {
      c.innerHTML = '<strong>' + esc(m.title || "Book the Evaluation") + '</strong><p>' + esc(m.text || "Three fields. A person replies within one business day to set the time.") + '</p>' +
        '<form class="agent-book"><input name="name" placeholder="Your name" required aria-label="Your name"><input name="email" type="email" placeholder="Work email" required aria-label="Work email"><input name="company" placeholder="Company" required aria-label="Company"><input type="hidden" name="subject" value="Evaluation request via the site agent"><input type="hidden" name="from_name" value="AI Native website agent"><button class="btn btn-primary btn-sm" type="submit">Book it</button><span class="agent-book-status" role="status"></span></form>';
      var f = c.querySelector("form");
      f.addEventListener("submit", function (e) {
        e.preventDefault(); var st = f.querySelector(".agent-book-status"); var data = new FormData(f); var a = AGENT.config;
        if (a.formEndpoint && a.formAccessKey) {
          data.append("access_key", a.formAccessKey);
          fetch(a.formEndpoint, { method: "POST", body: data, headers: { Accept: "application/json" } }).then(function (r) { return r.json(); }).then(function (j) { if (!j || j.success === false) throw 0; st.textContent = "Received. A person will reply to set the time."; f.querySelectorAll("input,button").forEach(function (x) { x.disabled = true; }); }).catch(function () { st.textContent = "That did not send — please use the Evaluation page."; });
        } else if (a.formEmail) {
          var lines = []; data.forEach(function (v, k) { if (k !== "subject" && k !== "from_name") lines.push(k + ": " + v); });
          window.location.href = "mailto:" + a.formEmail + "?subject=" + encodeURIComponent("Evaluation request") + "&body=" + encodeURIComponent(lines.join("\n")); st.textContent = "Your email app should open with the request.";
        } else st.textContent = "The form is not connected yet.";
      });
    }
    return c;
  }
  function typing(on) { each(function (ui) { var t = ui.log.querySelector(".agent-typing"); if (on && !t) { t = h("div", "agent-msg is-agent agent-typing", '<div class="agent-bubble"><span></span><span></span><span></span></div>'); ui.log.appendChild(t); ui.log.scrollTop = ui.log.scrollHeight; } else if (!on && t) t.remove(); }); }
  function renderAll() { each(function (ui) { ui.log.innerHTML = ""; }); history.forEach(function (m) { addMsg(m.msg, m.who); }); }
  function each(fn) { Object.keys(els).forEach(function (k) { fn(els[k]); }); }

  // ---------- conversation ----------
  function send(text) {
    if (busy) return;
    var m = { type: "text", text: text }; history.push({ who: "user", msg: m }); save(); addMsg(m, "user");
    busy = true; typing(true);
    var p = AGENT.config.mode === "live" && AGENT.config.endpoint ? live(text) : Promise.resolve(demo(text));
    p.then(function (msgs) { setTimeout(function () { typing(false); busy = false; reply(msgs); }, 350); })
     .catch(function () { typing(false); busy = false; reply([{ type: "text", text: "I can't reach my systems right now. A person can help:" }, { type: "card", kind: "handoff" }]); });
  }
  function reply(msgs) { msgs.forEach(function (m) { history.push({ who: "agent", msg: m }); addMsg(m, "agent"); }); save(); }
  function live(text) {
    return fetch(AGENT.config.endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ session_id: sessionId(), message: text, page: { url: location.href, title: doc.title }, history: history.slice(-12).map(function (x) { return { who: x.who, text: x.msg.text || "" }; }) }) })
      .then(function (r) { if (!r.ok) throw new Error("agent"); return r.json(); }).then(function (j) { return (j && j.messages) || [{ type: "text", text: "Sorry — say that again?" }]; });
  }

  // ---------- demo responder (the site's own answers; replaced by the live agent) ----------
  var ANSWERS = [
    [/cost|price|pric|expensive|how much|fee/, "Far less than the person you would otherwise have hired — for far more than one person's work. You pay one firm one predictable price for a workforce that covers every department and works around the clock. The Evaluation ends with your number in writing.", [{ type: "chips", options: ["Book the Evaluation", "What is the Evaluation?"] }]],
    [/evaluation|what is the eval|what happens/, "The Evaluation is two hours with you and your leadership. Department by department, we map the work done by hand today and show you what an agent takes, what it is tied into, and who checks it. You leave with the map, the number, and the timeline — in writing.", [{ type: "card", kind: "link", title: "How it works", text: "The four stages in detail.", href: rel("how-it-works.html"), cta: "Read" }]],
    [/hand ?off|person|human|real|talk to someone|speak/, "Whenever someone asks, whenever I'm unsure, and on any topic a client lists, I hand to a person. On this site, a person is one click away.", [{ type: "card", kind: "handoff" }]],
    [/embarrass|customers hate|machine|robot/, "Every agent says what it is in its first sentence, answers only from the business's own data, books in under a minute, and hands to a person the moment someone asks. Before it speaks to a customer, the owner approves its first hundred replies."],
    [/staff use|my people|adoption|train/, "Training is inside the Install. Nothing goes live until your staff can run it — and the first thing every person gets is a Chief of Staff agent, so the first thing the workforce does is give them their day back."],
    [/break|support|who do i call/, "You call us. One firm, one number. The Management stage exists for exactly this: we run it, update it, and answer the phone."],
    [/data|secure|privacy/, "Agents work inside the systems you already use and are tied into them under the Install agreement. What stays where is written down before anything is installed."],
    [/replace|headcount|fire|lay ?off/, "No. Agents take the routine; people do the work only people can do. The business grows without hiring."],
    [/stop|cancel|quit|contract/, "Management ends and the agents are retired from your systems. Nothing about your business is held hostage; the terms are in the agreement you sign before the Install."],
    [/how long|timeline|when/, "We give you the timeline in writing at the end of the Evaluation, and we do not install anything until your staff can run it."],
    [/chatbot|chatgpt|zapier|we already/, "Those are tools and bolt-ons. This is a workforce for the whole company, with a firm accountable for it."],
    [/too small|solo|just me|one person/, "A solo operator gets the first staff they have ever had — a Chief of Staff agent and a Customer Service agent to start. The Evaluation is where we map it."],
    [/software|tools?\b|tech|system|crm|quickbooks|calendly|gorgias|integrat|stack|app(s|lication)?\b/, "Agents need tools, and we bring them. If you like your CRM, your phones, your store, they stay. Where a tool is missing — chat on your site, a scheduling calendar, a bookkeeping system, a customer-service inbox — we bring one that is ready for agents, set it up, and train you. It is in the plan and the price.", [{ type: "card", kind: "link", title: "The tools you keep, we bring, we make", text: "How the Install sets them up.", href: rel("how-it-works.html#tools"), cta: "Read" }]],
    [/hvac|plumb|roof|dental|dentist|medical|vet|salon|spa|gym|fitness|auto|real estate|mortgage|insurance|tutor|home service/, "For a business like that we usually install a voice Customer Service agent that answers every call and books it, a Sales agent for speed-to-lead and estimate follow-up, a Bookkeeping agent, and a Chief of Staff agent for the owner and the office. Every missed call stops being a job for somebody else.", [{ type: "card", kind: "link", title: "We serve people in person", text: "Where the day goes, what we install, what the Report shows.", href: rel("businesses/serve-people-in-person.html"), cta: "See the map" }]],
    [/distribut|manufactur|wholesale|supplier|packaging|industrial|rfq|purchase order|\bpo\b/, "For a business like that: a Customer Service agent that reads emailed POs into the order system and answers spec questions day and night, a Sales agent that turns RFQs into quotes in the same hour, an Operations agent for inventory and vendors, a Bookkeeping agent, and a Chief of Staff agent for every desk.", [{ type: "card", kind: "link", title: "We supply other businesses", text: "Orders stop waiting for Monday.", href: rel("businesses/supply-other-businesses.html"), cta: "See the map" }]],
    [/agency|law|attorney|account(ing|ant)|consult|staffing|contractor|cleaning|landscap|logistic|\bmsp\b|it provider/, "For a firm like that: a Sales agent that answers every inquiry in minutes and drafts proposals from your own pricing, a Customer Service agent for client updates, a Bookkeeping agent for billing and collections, and a Chief of Staff agent for every desk.", [{ type: "card", kind: "link", title: "We serve other businesses", text: "We win the work we have time to bid — now all of it.", href: rel("businesses/serve-other-businesses.html"), cta: "See the map" }]],
    [/e-?commerce|dtc|shopify|amazon|retail|store|subscription|brand|order status|returns/, "For a brand like that: a Customer Service agent for order status, returns, and product questions across chat and email, a Marketing agent for creative and lifecycle email and SMS, an Operations agent for inventory and listings, a Bookkeeping agent, and a Chief of Staff agent for every desk.", [{ type: "card", kind: "link", title: "We sell products to people", text: "The inbox stops being where the day goes.", href: rel("businesses/sell-products-to-people.html"), cta: "See the map" }]],
    [/what are you|are you a person|are you human|are you ai|who are you/, "I'm an AI agent, powered by AI Native — the Customer Service agent we install for clients, working for AI Native itself. I answer questions about the firm and book the Evaluation. Want a person? Type person."],
    [/report|results|numbers|kpi|measure/, "The Report shows three things, every time: the additional work completed, the hours returned to your team, and how the business is performing — measured or labelled a target, never rounded.", [{ type: "card", kind: "link", title: "The Report", text: "What is measured and how.", href: rel("report.html"), cta: "Read" }]],
    [/workforce|agents?\b|chief of staff|what do you install|departments?/, "A Chief of Staff agent for every worker, and an agent for every function that runs by hand today — sales, customer service, bookkeeping, marketing, operations, HR, IT. Those are examples; the Evaluation maps every department you have.", [{ type: "card", kind: "link", title: "Your AI workforce", text: "What each agent does.", href: rel("workforce.html"), cta: "Read" }]],
    [/book|schedule|sign ?up|get started|meet|call me/, "Let's set it up.", [{ type: "card", kind: "book" }]],
    [/founder|leader|leadership|who runs|about you|operators|who will|who are we talking|experience/, "AI Native is led by a senior leadership team that has built and run businesses of every kind and size together for 35 years. A senior leader who has run a business like yours leads your Evaluation — not a salesperson, not a junior consultant — and stays accountable through the Install.", [{ type: "card", kind: "link", title: "The senior leadership team", text: "Operators, not vendors.", href: rel("about.html"), cta: "Read" }]],
    [/thank|thanks|great|ok\b|okay/, "Any time. Anything else, or shall I book the Evaluation?", [{ type: "chips", options: ["Book the Evaluation", "What would you install for us?"] }]]
  ];
  function rel(p) { var depth = (location.pathname.match(/\/businesses\//) ? "../" : ""); return depth + p; }
  function demo(text) {
    var t = text.toLowerCase(), out = [];
    for (var i = 0; i < ANSWERS.length; i++) { if (ANSWERS[i][0].test(t)) { out.push({ type: "text", text: ANSWERS[i][1] }); (ANSWERS[i][2] || []).forEach(function (m) { out.push(m); }); return out; } }
    return [{ type: "text", text: "I can answer questions about the Evaluation, the Install, the workforce, the Report, and the four kinds of business we serve — or get you a person. What would you like to know?" }, { type: "chips", options: ["What does the Evaluation cost?", "What would you install for us?", "Get a person"] }];
  }

  // ---------- mounting ----------
  function mount(host) { var ui = build(host, true); els.inline = ui; inlineHost = host; if (history.length) renderAll(); else reply(GREETING); }
  function open() {
    if (!els.floating) { var host = h("div", "agent-host", ""); doc.body.appendChild(host); els.floating = build(host, false); if (history.length) renderAll(); else reply(GREETING); }
    els.floating.panel.setAttribute("data-open", "true"); doc.body.setAttribute("data-agent-open", "true"); els.launcher.setAttribute("aria-expanded", "true"); setTimeout(function () { els.floating.ta.focus(); }, 50);
  }
  function close() { if (!els.floating) return; els.floating.panel.removeAttribute("data-open"); doc.body.removeAttribute("data-agent-open"); els.launcher.setAttribute("aria-expanded", "false"); els.launcher.focus(); }
  function launcher() {
    var b = h("button", "agent-launcher", '<span class="agent-launcher-badge">' + BADGE + '</span><span class="agent-launcher-label">Ask our agent</span>');
    b.type = "button"; b.setAttribute("aria-expanded", "false"); b.setAttribute("aria-label", "Ask the AI Native service agent");
    b.addEventListener("click", function () { if (els.floating && els.floating.panel.getAttribute("data-open") === "true") close(); else open(); });
    doc.body.appendChild(b); els.launcher = b;
    doc.addEventListener("keydown", function (e) { if (e.key === "Escape" && els.floating && els.floating.panel.getAttribute("data-open") === "true") close(); });
  }
  doc.addEventListener("DOMContentLoaded", function () {
    launcher();
    var inline = doc.getElementById("agent-inline"); if (inline) mount(inline);
    doc.querySelectorAll("[data-agent-open]").forEach(function (a) { a.addEventListener("click", function (e) { e.preventDefault(); open(); var q = a.getAttribute("data-agent-open"); if (q) setTimeout(function () { send(q); }, 200); }); });
  });
})();
