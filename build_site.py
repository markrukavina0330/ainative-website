#!/usr/bin/env python3
"""ainative.ai — static site generator. Output: ./site (deployable as-is at the domain root)."""
import os, json, datetime

OUT = "site"
os.makedirs(f"{OUT}/css", exist_ok=True); os.makedirs(f"{OUT}/js", exist_ok=True); os.makedirs(f"{OUT}/businesses", exist_ok=True)

# ---------------- go-live configuration (founders supply; empty values hide the element) ----------------
CFG = {
    "SITE_URL": "https://ainative.ai",
    "FORM_ENDPOINT": "",          # e.g. https://formspree.io/f/xxxxxxxx  — the Evaluation form POSTs here; empty = mailto fallback
    "CONTACT_EMAIL": "",          # e.g. evaluation@ainative.ai
    "CONTACT_PHONE": "",          # e.g. +1 480 000 0000  (display) — leave empty to hide
    "CALENDAR_URL": "",           # e.g. https://cal.com/ainative/evaluation — leave empty to hide the scheduling button
    "ANALYTICS_SNIPPET": "",      # optional: a privacy-respecting analytics tag
    "AGENT_WIDGET_SNIPPET": "",   # optional: the AI Native service agent widget embed for this site
    "REPLY_WITHIN": "one business day",  # what the founders commit to for a reply
}

LOCKUP = open(f"{OUT}/assets/lockup-horizontal.svg").read()
STACKED = open(f"{OUT}/assets/lockup-stacked.svg").read()
BADGE = open(f"{OUT}/assets/badge.svg").read()
BADGE1 = open(f"{OUT}/assets/badge-1c.svg").read()
URLLOCK = open(f"{OUT}/assets/url-lockup.svg").read()
TOKENS = open("phase3p2/tokens/tokens.css").read()

NAV = [("how-it-works.html", "How it works"), ("workforce.html", "Your AI workforce"),
       ("businesses/", "Businesses like yours", [("businesses/b2b-service.html", "B2B service"), ("businesses/b2b-product.html", "B2B product"), ("businesses/b2c-service.html", "B2C service"), ("businesses/b2c-product.html", "B2C product")]),
       ("report.html", "The Report"), ("answers.html", "Straight answers"), ("about.html", "About")]


# ---------------- layout ----------------
def head(title, desc, rel, path, og=None):
    canon = f'{CFG["SITE_URL"]}/{path}'.replace("/index.html", "/")
    return f'''<!doctype html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="AI Native"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{CFG["SITE_URL"]}/assets/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1E1F22" media="(prefers-color-scheme: dark)"><meta name="theme-color" content="#F6F4EE" media="(prefers-color-scheme: light)">
<link rel="icon" href="{rel}assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="{rel}assets/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="{rel}assets/apple-touch-icon.png"><link rel="manifest" href="{rel}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Atkinson+Hyperlegible+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}css/site.css">
{('<script type="application/ld+json">' + open("site/entity.jsonld").read() + '</script>') if path == "index.html" and os.path.exists("site/entity.jsonld") else ""}
<script>(function(){{try{{var t=localStorage.getItem("an-theme");if(t)document.documentElement.setAttribute("data-theme",t);}}catch(e){{}}}})();</script>
{CFG["ANALYTICS_SNIPPET"]}
</head>'''


def header(rel, current):
    items = []
    for it in NAV:
        if len(it) == 3:
            sub = "".join(f'<li><a href="{rel}{h}"{" aria-current=\"page\"" if h == current else ""}>{l}</a></li>' for h, l in it[2])
            items.append(f'<li class="has-sub"><button class="nav-sub-toggle" aria-expanded="false" aria-controls="sub-businesses">{it[1]}<svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button><ul class="sub" id="sub-businesses">{sub}</ul></li>')
        else:
            items.append(f'<li><a href="{rel}{it[0]}"{" aria-current=\"page\"" if it[0] == current else ""}>{it[1]}</a></li>')
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header" id="top">
  <div class="container header-row">
    <a class="brand" href="{rel}index.html" aria-label="AI Native home">{LOCKUP}</a>
    <nav class="site-nav" id="site-nav" aria-label="Primary">
      <ul>{"".join(items)}</ul>
      <div class="nav-mobile-cta"><a class="btn btn-primary" href="{rel}evaluation.html">Book the Evaluation</a></div>
    </nav>
    <div class="header-actions">
      <a class="btn btn-primary cta" href="{rel}evaluation.html"><span class="cta-long">Book the Evaluation</span><span class="cta-short">Book</span></a>
      <button class="menu-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>'''


def footer(rel):
    contact = []
    if CFG["CONTACT_EMAIL"]: contact.append(f'<li><a href="mailto:{CFG["CONTACT_EMAIL"]}">{CFG["CONTACT_EMAIL"]}</a></li>')
    if CFG["CONTACT_PHONE"]: contact.append(f'<li><a href="tel:{CFG["CONTACT_PHONE"].replace(" ", "")}">{CFG["CONTACT_PHONE"]}</a></li>')
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="{rel}index.html" class="url-lockup" aria-label="ainative.ai">{URLLOCK}</a>
        <p class="footer-tag">Your business, AI Native.</p>
        <p class="footer-support">Every worker. Every department. Done for you.</p>
      </div>
      <div><h2 class="footer-h">The work</h2><ul><li><a href="{rel}how-it-works.html">How it works</a></li><li><a href="{rel}workforce.html">Your AI workforce</a></li><li><a href="{rel}report.html">The Report</a></li><li><a href="{rel}ai-native-company.html">AI Native Company</a></li></ul></div>
      <div><h2 class="footer-h">Businesses like yours</h2><ul><li><a href="{rel}businesses/b2b-service.html">B2B service</a></li><li><a href="{rel}businesses/b2b-product.html">B2B product</a></li><li><a href="{rel}businesses/b2c-service.html">B2C service</a></li><li><a href="{rel}businesses/b2c-product.html">B2C product</a></li></ul></div>
      <div><h2 class="footer-h">The firm</h2><ul><li><a href="{rel}about.html">About</a></li><li><a href="{rel}answers.html">Straight answers</a></li><li><a href="{rel}agents.html">How our agents identify themselves</a></li><li><a href="{rel}evaluation.html">Book the Evaluation</a></li>{"".join(contact)}</ul></div>
    </div>
    <div class="footer-legal">
      <p>AI Native™ agents identify themselves as AI agents in the first sentence of every conversation. Figures on this site are measured results or are labelled as targets.</p>
      <p>© <span id="year"></span> AI Native. AI Native is a trademark. <a href="{rel}privacy.html">Privacy</a> · <a href="{rel}terms.html">Terms</a> · <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Switch colour theme">Appearance: <span id="theme-label">Auto</span></button></p>
    </div>
  </div>
  <div class="site-band" aria-hidden="true"></div>
</footer>
{CFG["AGENT_WIDGET_SNIPPET"]}
<script src="{rel}js/site.js" defer></script>
</body></html>'''


def cta_panel(rel, title="Book the Evaluation.", body="We meet with you and your leadership, map every department's manual work, and show you where an agent workforce fits. You leave with the number and the timeline in writing."):
    return f'''<section class="cta-panel has-band" aria-labelledby="cta-h">
  <div class="cta-inner">
    <div><h2 id="cta-h">{title}</h2><p>{body}</p></div>
    <div class="cta-actions"><a class="btn btn-on-dark" href="{rel}evaluation.html">Book the Evaluation</a><a class="link-on-dark" href="{rel}how-it-works.html">See how the Install works</a></div>
  </div>
</section>'''


def page(path, title, desc, body, current=None):
    depth = path.count("/"); rel = "../" * depth
    html = head(title, desc, rel, path) + "\n<body>\n" + header(rel, current or path) + f'\n<main id="main">\n{body}\n</main>\n' + footer(rel)
    open(f"{OUT}/{path}", "w").write(html)


# ---------------- reusable blocks ----------------
def roster_table(rel, rows=None, note=True):
    rows = rows or [("Every desk", "Email, scheduling, meeting notes, follow-ups, status", "Chief of Staff agent"), ("Sales", "Speed-to-lead, prospecting, quotes, follow-up, CRM hygiene", "Sales agent"),
                    ("Customer service", "Calls, chat, tickets, order status, booking, reviews", "Customer Service agent"), ("Finance and bookkeeping", "AP and AR, invoicing, collections, reconciliation, month-end", "Bookkeeping agent"),
                    ("Marketing", "Content, campaigns, ads, SEO, email and SMS, reporting", "Marketing agent"), ("Operations", "Orders, inventory, purchasing, vendor communication", "Operations agent"),
                    ("HR and people", "Screening, scheduling, onboarding, policy questions", "HR agent"), ("IT and legal", "Tier-1 helpdesk, access, first-pass contract review", "IT Helpdesk agent")]
    trs = "".join(f'<tr><th scope="row" data-label="Department">{a}</th><td data-label="The manual work">{b}</td><td data-label="The agent"><span class="agent-chip"><span class="agent-badge">{BADGE1}</span>{c}</span></td></tr>' for a, b, c in rows)
    n = '<p class="note">These are examples. The workforce covers every department you have.</p>' if note else ""
    return f'<div class="table-wrap"><table class="roster"><thead><tr><th scope="col">Department</th><th scope="col">The manual work</th><th scope="col">The agent that takes it</th></tr></thead><tbody>{trs}</tbody></table>{n}</div>'


def kpi(label, value, delta, target=False):
    return f'<div class="kpi"><span class="kpi-label">{label}</span><span class="kpi-value">{value}</span><span class="kpi-delta{" is-target" if target else ""}">{delta}</span></div>'


def results_panel(compact=False):
    return f'''<div class="results has-band" role="group" aria-label="Sample results, design targets until measured">
  <div class="results-head"><span>Results this month</span><span class="results-note">design targets until measured</span></div>
  <dl class="results-list">
    <div><dt>Calls answered</dt><dd>1,240</dd></div>
    <div><dt>Leads answered in minutes</dt><dd>312</dd></div>
    <div><dt>Meetings booked</dt><dd>41</dd></div>
    <div><dt>Hours returned to the team</dt><dd>418.5</dd></div>
  </dl>
</div>'''


def chart_before_after(cats, before, after, title):
    mx = max(before) * 1.12; w = 600; h = 240; gw = w / len(cats); bars = []
    for i, c in enumerate(cats):
        bx = 30 + i * gw + gw * 0.18; bw = gw * 0.26; hb = before[i] / mx * 180; ha = after[i] / mx * 180
        bars.append(f'<rect x="{bx:.0f}" y="{200-hb:.0f}" width="{bw:.0f}" height="{hb:.0f}" rx="3" class="bar-before"/><rect x="{bx+bw+6:.0f}" y="{200-ha:.0f}" width="{bw:.0f}" height="{ha:.0f}" rx="3" class="bar-after"/>'
                    f'<text x="{bx:.0f}" y="{200-hb-6:.0f}" class="bar-val">{before[i]}</text><text x="{bx+bw+6:.0f}" y="{200-ha-6:.0f}" class="bar-val is-after">{after[i]}</text><text x="{bx:.0f}" y="222" class="bar-cat">{c}</text>')
    grid = "".join(f'<line x1="30" x2="{w+30}" y1="{200-k*45}" y2="{200-k*45}" class="gridline"/>' for k in range(5))
    return f'''<figure class="chart"><figcaption>{title}</figcaption><svg viewBox="0 0 {w+60} {h}" role="img" aria-label="{title}">{grid}{"".join(bars)}</svg><div class="legend"><span><i class="sw sw-before"></i>Manual</span><span><i class="sw sw-after"></i>AI Native</span><span class="legend-note">design targets until measured</span></div></figure>'''


def eval_form(rel, compact=False):
    action = CFG["FORM_ENDPOINT"] or "#"
    fields = f'''
      <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" type="text" autocomplete="name" required></div>
      <div class="field"><label for="f-company">Company</label><input id="f-company" name="company" type="organization" autocomplete="organization" required></div>
      <div class="field"><label for="f-email">Work email</label><input id="f-email" name="email" type="email" autocomplete="email" inputmode="email" required></div>
      <div class="field"><label for="f-phone">Phone <span class="opt">optional</span></label><input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel"></div>'''
    more = "" if compact else f'''
      <div class="field"><label for="f-category">What kind of business</label><select id="f-category" name="category" required><option value="">Choose one</option><option>B2B service — we sell expertise and hours to businesses</option><option>B2B product — we make or distribute products for businesses</option><option>B2C service — we serve consumers in person or on site</option><option>B2C product — we sell products to consumers</option><option>More than one of these</option></select></div>
      <div class="field"><label for="f-size">People in the company</label><select id="f-size" name="size" required><option value="">Choose one</option><option>Just me</option><option>2–10</option><option>11–50</option><option>51–200</option><option>201–500</option></select></div>
      <div class="field field-wide"><label for="f-pain">Where does the day go? <span class="opt">the manual work you would hand off first</span></label><textarea id="f-pain" name="pain" rows="3"></textarea></div>
      <div class="field field-wide"><label for="f-when">Good times to talk <span class="opt">optional</span></label><input id="f-when" name="when" type="text" placeholder="e.g. mornings, Tuesday or Thursday"></div>'''
    return f'''<form class="eval-form{" is-compact" if compact else ""}" action="{action}" method="POST" data-endpoint="{CFG["FORM_ENDPOINT"]}" data-mailto="{CFG["CONTACT_EMAIL"]}" novalidate>
      <input type="hidden" name="_subject" value="Evaluation request from ainative.ai"><input type="text" name="_gotcha" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="form-grid">{fields}{more}</div>
      <div class="form-actions"><button class="btn btn-primary btn-lg" type="submit">Book the Evaluation</button><p class="form-note">A person replies within {CFG["REPLY_WITHIN"]}. No newsletter, no drip sequence.</p></div>
      <p class="form-status" role="status" aria-live="polite"></p>
    </form>'''


def straight_answers(rel, limit=None, ids=True):
    qa = [("embarrass", "Will it embarrass us in front of customers?", "Every agent says what it is in its first sentence, answers only from your data, books in under a minute, and hands to a person the moment someone asks. Before it speaks to a single customer, you approve its first hundred replies."),
          ("people", "Will my people use it?", "Training is inside the Install. Nothing goes live until your staff can run it, and the first thing every person gets is a Chief of Staff agent — so the first thing the workforce does is give them their day back."),
          ("cost", "What does it cost against a hire?", "It is priced against the person you would otherwise have hired. The Evaluation ends with the number in writing. There is no price list on this site because there is no standard business."),
          ("breaks", "Who do I call when it breaks?", "Us. One firm, one number. The Management stage exists for exactly this: we run it, update it, and answer the phone."),
          ("get-back", "What do I get back?", "The Report — additional work completed, hours returned to the team, and how the business is performing — in your own figures, on the schedule set in the engagement."),
          ("replace", "Is this replacing my staff?", "No. Agents take the routine; people do the work only people can do. The business grows without hiring."),
          ("data", "What about our data?", "Agents work inside the systems you already use and are tied into them under the Install agreement. What stays where is written down before anything is installed."),
          ("chatbot", "We already tried a chatbot. We use ChatGPT.", "Those are tools and bolt-ons. This is a workforce for the whole company, with a firm accountable for it."),
          ("small", "We're too small. Or too complicated.", "A solo operator gets the first staff they have ever had. A 300-person distributor gets an agent in every department. The Evaluation is where complicated gets mapped."),
          ("long", "How long does it take?", "We give you the timeline in writing at the end of the Evaluation, and we do not install anything until your staff can run it."),
          ("systems", "Do we have to change our software?", "No. The agents are tied into the CRM, the accounting system, the phone system, and the store you already use. If a system is the bottleneck, the Evaluation will say so."),
          ("stop", "What happens if we stop?", "Management ends, the agents are retired from your systems, and the AI Native Company badge is withdrawn. Nothing about your business is held hostage; the terms are in the agreement you sign before the Install."),
          ("own", "Who is accountable?", "AI Native. The founders lead the Evaluation, the firm does the Install, and the firm manages the workforce. You have one party to call, and it is us.")]
    if limit: qa = qa[:limit]
    return "".join(f'<details class="answer"{" id=" + chr(34) + i + chr(34) if ids else ""}><summary><h3>{q}</h3></summary><p>{a}</p></details>' for i, q, a in qa)


# ---------------- pages ----------------
def build_home():
    rel = ""
    body = f'''
<section class="hero">
  <div class="container hero-grid">
    <div class="hero-copy">
      <h1>AI, built into your business.</h1>
      <p class="lead">A complete AI workforce for every worker in every department — designed, installed, trained, and managed for you.</p>
      <div class="hero-actions"><a class="btn btn-primary btn-lg" href="evaluation.html">Book the Evaluation</a><a class="btn btn-tertiary btn-lg" href="how-it-works.html">See how the Install works</a></div>
    </div>
    <div class="hero-visual">{results_panel()}</div>
  </div>
</section>

<section class="section" aria-labelledby="day-h">
  <div class="container">
    <h2 id="day-h">Where the day goes.</h2>
    <p class="section-lead">The owner's words, one per kind of business.</p>
    <div class="grid-4 owners">
      <a class="owner" href="businesses/b2b-service.html"><span class="eyebrow">B2B service</span><span class="owner-line">“We win the work we have time to bid.”</span></a>
      <a class="owner" href="businesses/b2b-product.html"><span class="eyebrow">B2B product</span><span class="owner-line">“Orders wait for Monday.”</span></a>
      <a class="owner" href="businesses/b2c-service.html"><span class="eyebrow">B2C service</span><span class="owner-line">“Every missed call is a job for somebody else.”</span></a>
      <a class="owner" href="businesses/b2c-product.html"><span class="eyebrow">B2C product</span><span class="owner-line">“The inbox is where our day goes.”</span></a>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="manual-h">
  <div class="container">
    <h2 id="manual-h">Manual. Bolt-on. AI Native.</h2>
    <div class="grid-3 panels">
      <div class="panel"><h3>Manual</h3><p>People on phones and keyboards doing the books, the leads, the customer questions, and the marketing by hand.</p></div>
      <div class="panel"><h3>Bolt-on</h3><p>A chatbot here, an AI dialer there, an AI feature inside the accounting software. Twelve logins. Nobody accountable.</p></div>
      <div class="panel panel-ink has-band"><div class="panel-badge">{BADGE}</div><h3>AI Native</h3><p>A complete AI workforce for every worker in every department — designed, installed, trained, and managed by one firm.</p></div>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="roster-h">
  <div class="container">
    <h2 id="roster-h">Your AI workforce.</h2>
    <p class="section-lead">A Chief of Staff agent for every worker, and an agent for every function that runs by hand today.</p>
    {roster_table(rel)}
    <p class="more"><a href="workforce.html">What each agent does, and how it works with your people</a></p>
  </div>
</section>

<section class="section" aria-labelledby="how-h">
  <div class="container">
    <h2 id="how-h">How it works.</h2>
    <ol class="steps">
      <li><span class="step-n">1</span><h3>Evaluate</h3><p>We meet with you and your leadership and map every department's manual work.</p></li>
      <li><span class="step-n">2</span><h3>Install</h3><p>We design, configure, and set up the workforce, and train your staff to run it.</p></li>
      <li><span class="step-n">3</span><h3>Manage</h3><p>We run it, update it, and support adoption over time.</p></li>
      <li><span class="step-n">4</span><h3>Report</h3><p>You see additional work completed, hours returned, and how the business performs.</p></li>
    </ol>
    <p class="promise">Nothing is installed until your staff can run it.</p>
    <p class="more"><a href="how-it-works.html">The four stages in detail</a></p>
  </div>
</section>

<section class="section" aria-labelledby="netnew-h">
  <div class="container">
    <h2 id="netnew-h">Work you could never staff.</h2>
    <ul class="dots grid-2">
      <li>Website chat that answers around the clock and writes the CRM</li>
      <li>Every call answered and booked, 24/7</li>
      <li>Every lead answered in minutes</li>
      <li>Every quote and estimate followed up</li>
      <li>Every account contacted for reorder</li>
      <li>Every dormant customer reactivated</li>
    </ul>
    <p class="note">Examples, not the list — the work that never got done because it needed a person you could not afford.</p>
  </div>
</section>

<section class="section" aria-labelledby="biz-h">
  <div class="container">
    <h2 id="biz-h">Businesses like yours.</h2>
    <div class="grid-4 cards">
      <a class="card" href="businesses/b2b-service.html"><h3>B2B service</h3><p>Every inquiry answered in minutes. Every proposal drafted from your own pricing.</p><span class="card-link">See the map</span></a>
      <a class="card" href="businesses/b2b-product.html"><h3>B2B product</h3><p>POs read the moment they arrive. Quotes in the same hour.</p><span class="card-link">See the map</span></a>
      <a class="card" href="businesses/b2c-service.html"><h3>B2C service</h3><p>Every call answered and booked. Every estimate followed up.</p><span class="card-link">See the map</span></a>
      <a class="card" href="businesses/b2c-product.html"><h3>B2C product</h3><p>Order status, returns, and product questions answered instantly.</p><span class="card-link">See the map</span></a>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="ops-h">
  <div class="container operators">
    <div class="operators-photo has-band" role="img" aria-label="Photograph: the founders in a client's workplace — to be supplied"></div>
    <div>
      <h2 id="ops-h">Operators, not vendors.</h2>
      <p>Mark Rukavina and Steve Krell have spent 35 years building companies from scratch in all four categories AI Native serves — across sales, marketing, technology, product, operations, customer service, finance, accounting, and bookkeeping. They know where the manual work piles up because they have done it. They lead every Evaluation.</p>
      <p class="more"><a href="about.html">About the firm</a></p>
    </div>
  </div>
</section>

<section class="section" aria-labelledby="report-h">
  <div class="container">
    <h2 id="report-h">The Report.</h2>
    <p class="section-lead">What you see, in your own numbers. A sample page; every figure is a design target until measured.</p>
    <div class="grid-4 kpis">{kpi("Calls answered", "1,240", "+18% vs last month")}{kpi("Leads answered in minutes", "312", "+22% vs last month")}{kpi("Meetings booked", "41", "+9% vs last month")}{kpi("Hours returned", "418.5", "target", True)}</div>
    {chart_before_after(["Sales", "Service", "Books", "Ops"], [38, 52, 30, 26], [9, 6, 4, 11], "Hours per week on manual work — before the Install and after")}
    <p class="more"><a href="report.html">What the Report measures and how</a></p>
  </div>
</section>

<section class="section" aria-labelledby="answers-h">
  <div class="container">
    <h2 id="answers-h">Straight answers.</h2>
    <div class="answers">{straight_answers(rel, limit=6, ids=False)}</div>
    <p class="more"><a href="answers.html">All the answers</a></p>
  </div>
</section>

<section class="section" aria-labelledby="book-h">
  <div class="container">
    <div class="book-panel has-band">
      <div class="book-copy"><h2 id="book-h">Book the Evaluation.</h2><p>We meet with you and your leadership, map every department, and show you where an agent workforce fits. You leave with the number and the timeline in writing.</p></div>
      {eval_form(rel, compact=True)}
    </div>
  </div>
</section>'''
    page("index.html", "AI Native™ — the AI workforce firm for small and medium-sized businesses", "AI Native designs, installs, trains, and manages a complete AI agent workforce for every worker in every department of a small or medium-sized business. Done for you.", body, "index.html")


def build_how():
    rel = ""
    body = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">How it works</span><h1>Four stages. One accountable firm.</h1><p class="lead">We evaluate the business, install the workforce, manage it over time, and report what changed — in your numbers.</p></div></section>
<section class="section"><div class="container stage-list">
  <article class="stage"><span class="step-n">1</span><div><h2>The Evaluation</h2><p>We meet with you and your leadership — the owner, and whoever runs the office, the books, sales, and service. Department by department we map the work that is done by hand today: the phones, the leads, the proposals, the orders, the invoices, the reminders, the follow-up nobody gets to. We show you which of it an agent takes, what it is tied into, and who checks it.</p><p><strong>What you leave with:</strong> the map of your manual work, the workforce we would install, the number, and the timeline — in writing.</p></div></article>
  <article class="stage"><span class="step-n">2</span><div><h2>The Install</h2><p>We design the workforce for your company and for each person in it, configure every agent on your own data — your pricing, your policies, your voice — and tie it into the systems you already use. Then we train your staff to run it. Training is not a step after the Install; it is inside it.</p><p><strong>The rule:</strong> nothing is installed until your staff can run it. Before an agent speaks to a customer, you approve its first hundred replies.</p></div></article>
  <article class="stage"><span class="step-n">3</span><div><h2>Management</h2><p>We run the workforce, update its configuration as your business changes, and support adoption — the second month is where most software fails and where our work starts. When something breaks, you call us. When an agent is unsure, it hands to a person and tells us.</p><p><strong>One number.</strong> One firm accountable for the whole workforce, not twelve vendors accountable for a login each.</p></div></article>
  <article class="stage"><span class="step-n">4</span><div><h2>The Report</h2><p>On the schedule set in the engagement you see what changed: additional work completed, hours returned to the team and what they went to, and how the business is performing on the AI Native way of operating. Every figure is measured or labelled a target. Nothing is rounded to look better.</p><p class="more"><a href="report.html">What the Report shows</a></p></div></article>
</div></section>
<section class="section section-alt"><div class="container">
  <h2>What the Evaluation is not.</h2>
  <div class="grid-3 panels">
    <div class="panel"><h3>Not a demo</h3><p>You will not watch a product. You will sit with operators who have run companies like yours and go through your departments one at a time.</p></div>
    <div class="panel"><h3>Not a sales pitch</h3><p>If the honest answer is that one department is worth doing and the rest are not, that is the answer you get. The map is yours either way.</p></div>
    <div class="panel"><h3>Not a commitment</h3><p>The Evaluation ends with a written plan. The Install begins only when your leadership signs it.</p></div>
  </div>
</div></section>
<section class="section"><div class="container">
  <h2>Who should be in the room.</h2>
  <p class="section-lead">The owner, and the people who carry the manual work: the office manager, the controller or bookkeeper, whoever runs sales and service. Two hours of their time in the Evaluation is what saves them the rest of the year.</p>
  <div class="answers">{straight_answers(rel, limit=4, ids=False)}</div>
</div></section>
{cta_panel(rel)}'''
    page("how-it-works.html", "How it works — the Evaluation, the Install, Management, the Report | AI Native", "AI Native's four stages: we evaluate the business with its leadership, install the AI workforce and train the staff, manage it over time, and report the results in your numbers.", body)


def build_workforce():
    rel = ""
    agents = [("Chief of Staff agent", "for every worker", "Handles communications and project assignments, triages and drafts email, keeps the calendar, writes meeting notes and follow-ups, and tracks status. Time on routine work becomes time on the projects only that person can do."),
              ("Sales agent", "sales", "Answers every lead in minutes, in writing and by voice, qualifies it, drafts the quote or proposal from your pricing and your past work, follows up until there is an answer, books the meeting, and keeps the CRM clean. A smaller, far more productive sales team."),
              ("Customer Service agent", "customer service", "Answers requests instantly and accurately across chat, email, and voice — inbound and outbound — tied into the CRM and the back office. Books, reschedules, answers order status, handles returns, requests and responds to reviews, and hands to a person the moment someone asks."),
              ("Bookkeeping agent", "finance, accounting, bookkeeping", "Runs AP and AR, invoicing, collections, expenses, and reconciliation; prepares payroll and sales tax; closes the month on time; and produces the KPI dashboard. Finance time moves from data entry to strategy."),
              ("Marketing agent", "marketing", "Drafts content and campaign creative, deploys ads, runs SEO and social, sends lifecycle email and SMS, manages reviews and reputation, tests creative at scale, and reports on all of it."),
              ("Operations agent", "operations", "Enters orders — including the ones that arrive as emailed POs — manages inventory and reorder points, handles purchasing and vendor communication, and keeps fulfillment and scheduling moving."),
              ("HR agent", "people", "Screens candidates, schedules interviews, prepares onboarding documents, tracks PTO, answers policy questions, and sends compliance reminders."),
              ("IT Helpdesk agent", "IT and legal", "Tier-1 helpdesk and access provisioning; first-pass contract review and renewal tracking, with anything material handed to a person.")]
    cards = "".join(f'<article class="agent-card"><div class="agent-card-head"><span class="agent-badge">{BADGE1}</span><h3>{n}</h3><span class="agent-dept">{d}</span></div><p>{b}</p></article>' for n, d, b in agents)
    body = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">Your AI workforce</span><h1>A Chief of Staff agent for every worker. An agent for every job that runs by hand.</h1><p class="lead">Designed for your company and for each person in it. Tied into the software you already use. Managed by one firm.</p></div></section>
<section class="section"><div class="container">
  <h2>The roster, by department.</h2>
  <div class="grid-2 agent-grid">{cards}</div>
  <p class="note">These are examples. The workforce covers every department you have, and every use — the Evaluation maps yours.</p>
</div></section>
<section class="section section-alt"><div class="container">
  <h2>Two kinds of work.</h2>
  <div class="grid-2 panels">
    <div class="panel"><h3>Work a person does today</h3><p>Moves to an agent that does it as well or better, and the person is freed for the work only a person can do. We measure the hours returned — and what they went to.</p></div>
    <div class="panel"><h3>Work that never got done</h3><p>Because it needed a person you could not afford: chat that answers at 2 a.m. and writes the CRM, every account contacted for reorder, every dormant customer reactivated, every estimate followed up. Now it gets done.</p></div>
  </div>
</div></section>
<section class="section"><div class="container">
  <h2>How agents work with your people.</h2>
  <ul class="dots grid-2">
    <li>Every agent says what it is in its first sentence, in chat and by voice.</li>
    <li>It hands to a person when asked, when it is unsure, and on any topic you list.</li>
    <li>You approve its first hundred replies before it speaks to a customer.</li>
    <li>It works inside your systems — the CRM, the books, the phones, the store — not beside them.</li>
    <li>Your people are trained to lead their agents; nothing goes live until they can.</li>
    <li>You see what it did, in the Report.</li>
  </ul>
  <p class="more"><a href="agents.html">How our agents identify themselves</a></p>
</div></section>
{cta_panel(rel, "Map your workforce.", "The Evaluation goes through your departments one at a time and shows you which work an agent takes, what it is tied into, and who checks it.")}'''
    page("workforce.html", "Your AI workforce — every worker, every department | AI Native", "A Chief of Staff agent for every worker and an agent for every function that runs by hand: sales, customer service, bookkeeping, marketing, operations, HR, IT. Examples, not the list.", body)


CATS = {
    "b2b-service": dict(title="B2B service", line="We win the work we have time to bid.", who="Law, accounting, agencies, IT providers, staffing, consultancies, commercial contractors, commercial cleaning and landscaping, logistics brokers — firms that sell expertise and hours to other businesses.",
        day=["Intake that waits for someone to be free", "Proposals and SOWs written at night", "Timesheets and billing that slip a week", "Client status updates nobody has time to send", "Collections that happen when the owner remembers"],
        install=[("Sales agent", "answers every inquiry in minutes and drafts proposals and SOWs from your pricing and your past work; a person approves every one"), ("Customer Service agent", "sends client updates before they ask and answers the routine requests"), ("Bookkeeping agent", "runs billing from the timesheets, invoices, reconciles, and runs collections"), ("Chief of Staff agent", "for every desk — the email, the calendar, the follow-ups")],
        netnew=["Instant inquiry response, around the clock", "Proactive client updates", "Automatic project and case summaries", "Dormant-client reactivation"],
        objection=("Our proposals are custom.", "They still are. The agent drafts from your pricing and your past proposals, in your voice, and a person approves every one before it goes out. What changes is that the draft is waiting for you instead of you waiting for the evening."),
        cats=["Sales", "Billing", "Updates", "Collections"], before=[36, 18, 14, 12], after=[8, 3, 2, 2]),
    "b2b-product": dict(title="B2B product", line="Orders wait for Monday.", who="Manufacturers, wholesalers and distributors, industrial suppliers, packaging, food producers selling to retail, software and hardware vendors — companies that make or move products for other businesses.",
        day=["POs that arrive by email and get re-keyed by hand", "RFQs quoted two days later", "Spec and availability questions answered when someone is free", "Vendor communication and reorder points managed from memory", "Invoicing and collections at the end of the day"],
        install=[("Customer Service agent", "reads emailed POs into the order system and answers spec and availability questions day and night"), ("Sales agent", "turns RFQs into quotes in the same hour and runs reorder outreach to every account"), ("Operations agent", "manages inventory, reorder points, purchasing, and vendor communication"), ("Bookkeeping agent", "AP, AR, invoicing, and collections"), ("Chief of Staff agent", "for every desk")],
        netnew=["24/7 spec and availability answers", "Quotes in minutes, not days", "Proactive reorder outreach to every account", "Backorder communication before the customer asks"],
        objection=("Our catalog is complicated.", "The Evaluation captures it. The agent answers only from your data — your catalog, your pricing, your lead times — and hands off anything it is not sure of. A complicated catalog is exactly the reason the questions pile up on two people's desks."),
        cats=["Orders", "Quotes", "Service", "Books"], before=[40, 22, 30, 20], after=[6, 4, 5, 4]),
    "b2c-service": dict(title="B2C service", line="Every missed call is a job for somebody else.", who="Dental, medical, and veterinary practices; home services — HVAC, plumbing, roofing, pool, landscaping; salons and spas; fitness studios; auto repair; real estate and mortgage; insurance agencies; tutoring — businesses that serve people in person or on site.",
        day=["Calls missed while the office is on another call", "Booking, reminders, and no-shows", "Estimates and quotes never followed up", "After-hours calls that go to voicemail", "Reviews, recalls, and reactivation that nobody has time for"],
        install=[("Customer Service voice agent", "answers every call and books it, tied to your scheduling software; hands to a person the moment someone asks"), ("Sales agent", "instant speed-to-lead on web forms, estimate and financing follow-up"), ("Bookkeeping agent", "invoicing, collections, month-end"), ("Chief of Staff agent", "for the owner and the office")],
        netnew=["Every call answered and booked, 24/7", "Review generation and response", "Recall and reactivation campaigns", "Estimate and financing follow-up until there is an answer"],
        objection=("My customers will hate talking to a machine.", "The agent says what it is in its first sentence, books the visit in under a minute, and hands to a person the moment someone asks. And it is there at 7 p.m. on a Friday in July, when the alternative is not a person — it is voicemail, and the job going to somebody else."),
        cats=["Phones", "Booking", "Estimates", "Books"], before=[45, 20, 15, 14], after=[4, 3, 2, 3]),
    "b2c-product": dict(title="B2C product", line="The inbox is where our day goes.", who="E-commerce and DTC brands, retailers, specialty stores, subscription boxes, makers, franchise retail — businesses that sell products to people.",
        day=["“Where is my order” all day, every day", "Returns, exchanges, and product questions", "Campaign creative and deployment by hand", "Inventory, purchasing, and marketplace listings", "Lifecycle email and SMS that goes out late or not at all"],
        install=[("Customer Service agent", "order status, returns, and product questions across chat and email, tied into the store and fulfillment"), ("Marketing agent", "creative, deployment, lifecycle email and SMS, and creative testing at scale"), ("Operations agent", "inventory, purchasing, and listings"), ("Bookkeeping agent", "reconciliation across the store, the marketplace, and the processor"), ("Chief of Staff agent", "for every desk")],
        netnew=["24/7 pre-sale chat with recommendations tied to live inventory", "Abandoned-cart conversations", "Review and UGC follow-up", "Personalized post-purchase"],
        objection=("Our brand voice is everything.", "It should be. The agent is trained on your voice and your policies during the Install, and you approve its first hundred replies before it speaks to a customer. It will sound like you at 2 a.m., which is more than a queue does."),
        cats=["Support", "Marketing", "Inventory", "Books"], before=[48, 30, 16, 14], after=[6, 8, 3, 3]),
}


def build_category(key):
    c = CATS[key]; rel = "../"
    day = "".join(f"<li>{d}</li>" for d in c["day"]); netnew = "".join(f"<li>{d}</li>" for d in c["netnew"])
    inst = "".join(f'<li><span class="agent-chip"><span class="agent-badge">{BADGE1}</span>{n}</span><span class="install-what">{w}</span></li>' for n, w in c["install"])
    others = "".join(f'<a class="card card-mini" href="{k}.html"><h3>{v["title"]}</h3><p>“{v["line"]}”</p></a>' for k, v in CATS.items() if k != key)
    body = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">Businesses like yours · {c["title"]}</span><h1>“{c["line"]}”</h1><p class="lead">{c["who"]}</p></div></section>
<section class="section"><div class="container grid-2 gap-lg">
  <div><h2>Where the day goes.</h2><ul class="dots">{day}</ul></div>
  <div><h2>What we install.</h2><ul class="install-list">{inst}</ul><p class="note">Examples from the roster, chosen in your Evaluation. Every department you have is covered.</p></div>
</div></section>
<section class="section section-alt"><div class="container">
  <h2>Work you could never staff.</h2>
  <ul class="dots grid-2">{netnew}</ul>
</div></section>
<section class="section"><div class="container grid-2 gap-lg">
  <div><h2>The first thing owners ask.</h2><h3 class="q">“{c["objection"][0]}”</h3><p>{c["objection"][1]}</p><p class="more"><a href="../answers.html">All the straight answers</a></p></div>
  <div><h2>What the Report shows.</h2>{chart_before_after(c["cats"], c["before"], c["after"], "Hours per week on manual work — before the Install and after")}</div>
</div></section>
<section class="section section-alt"><div class="container"><h2>Other businesses like yours.</h2><div class="grid-3">{others}</div></div></section>
{cta_panel(rel, "Map your departments.", "Two hours with your leadership. You leave with the map of your manual work, the workforce we would install, the number, and the timeline — in writing.")}'''
    page(f"businesses/{key}.html", f'{c["title"]} — “{c["line"]}” | AI Native', f'AI Native for {c["title"].lower()} businesses: where the day goes, what we install, the work you could never staff, and the first thing owners ask.', body)


def build_businesses_index():
    rel = "../"
    cards = "".join(f'<a class="card" href="{k}.html"><span class="eyebrow">{v["title"]}</span><h3>“{v["line"]}”</h3><p>{v["who"][:120].rsplit(",", 1)[0]}…</p><span class="card-link">See the map</span></a>' for k, v in CATS.items())
    body = f'''<section class="page-hero"><div class="container"><span class="eyebrow">Businesses like yours</span><h1>Every small and medium-sized business is one of four kinds. Often more than one.</h1><p class="lead">Choose the one that sounds like your day.</p></div></section>
<section class="section"><div class="container"><div class="grid-2 cards">{cards}</div></div></section>{cta_panel(rel)}'''
    page("businesses/index.html", "Businesses like yours — B2B service, B2B product, B2C service, B2C product | AI Native", "AI Native serves all four kinds of small and medium-sized business. Find where your day goes and what an AI workforce takes off it.", body, "businesses/")


def build_report():
    rel = ""
    body = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">The Report</span><h1>What changed, in your own numbers.</h1><p class="lead">Three things, every time: the additional work completed, the hours returned to your team, and how the business is performing on the AI Native way of operating.</p></div></section>
<section class="section"><div class="container">
  <div class="grid-4 kpis">{kpi("Calls answered", "1,240", "+18% vs last month")}{kpi("Leads answered in minutes", "312", "+22% vs last month")}{kpi("Meetings booked", "41", "+9% vs last month")}{kpi("Hours returned", "418.5", "target", True)}</div>
  <div class="grid-2 gap-lg">
    {chart_before_after(["Sales", "Service", "Books", "Ops"], [38, 52, 30, 26], [9, 6, 4, 11], "Hours per week on manual work — before the Install and after")}
    <div><h2>How it is counted.</h2><ul class="dots"><li><strong>Work completed</strong> — calls answered, leads answered, quotes sent, invoices out, orders entered: counted from your systems, not estimated.</li><li><strong>Hours returned</strong> — the time the manual work took before, measured in the Evaluation, against the time it takes your people now; and what those hours went to.</li><li><strong>Performance</strong> — the business measures you already watch: bookings, pipeline, days to close, collections, reviews.</li></ul><p class="note">Every figure on this page is a design target for illustration. Yours will be measured or labelled.</p></div>
  </div>
</div></section>
<section class="section section-alt"><div class="container grid-2 gap-lg">
  <div><h2>When you see it.</h2><p>On the schedule set in the engagement — and live, in the dashboard, whenever you want to look. The Report is the same components in print.</p></div>
  <div><h2>The rule behind every number.</h2><p>Measured, or labelled a target. Never rounded to look better. Never a percentage we have not measured. If a number is not there yet, the Report says so.</p></div>
</div></section>
{cta_panel(rel, "See what your numbers would look like.", "The Evaluation measures where the day goes today. That is the first line of your first Report.")}'''
    page("report.html", "The Report — what changed, in your own numbers | AI Native", "AI Native's Report shows additional work completed, hours returned to the team, and business performance — measured or labelled a target, never rounded.", body)


def build_answers():
    rel = ""
    body = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">Straight answers</span><h1>The questions owners ask before they sign. Answered in full sentences.</h1></div></section>
<section class="section"><div class="container answers answers-page">{straight_answers(rel)}</div></section>
{cta_panel(rel, "Ask us the one that is not here.", "The Evaluation is a conversation between operators. Bring the question.")}'''
    page("answers.html", "Straight answers — what owners ask before they sign | AI Native", "Will it embarrass us? Will my people use it? What does it cost against a hire? Who do I call when it breaks? Straight answers from AI Native.", body)


def build_about():
    rel = ""
    body = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">About</span><h1>Operators, not vendors.</h1><p class="lead">AI Native is the AI workforce firm. We design, install, train, and manage a complete AI agent workforce for every worker in every department of a small or medium-sized business — done for you, reported in your numbers.</p></div></section>
<section class="section"><div class="container operators">
  <div class="operators-photo has-band" role="img" aria-label="Photograph of Mark Rukavina and Steve Krell in a client's workplace — to be supplied"></div>
  <div>
    <h2>The founders.</h2>
    <p>Mark Rukavina and Steve Krell have spent 35 years building companies from scratch in all four categories AI Native serves — B2B service, B2B product, B2C service, and B2C product — across sales, marketing, technology, product development, operations, customer service, finance, accounting, and bookkeeping. They know exactly where the manual bottlenecks occur in every department and how AI agents remove them. They lead every Evaluation.</p>
    <!-- FOUNDER INPUT NEEDED: the companies built, the roles held, the outcomes the founders want on the record; one paragraph per founder; portrait photographs in the documentary style -->
    <div class="grid-2 founders">
      <div class="founder"><h3>Mark Rukavina</h3><p class="founder-role">Co-founder</p><p>Operator across all four categories. <!-- bio to be supplied --></p></div>
      <div class="founder"><h3>Steve Krell</h3><p class="founder-role">Co-founder</p><p>Operator across all four categories. <!-- bio to be supplied --></p></div>
    </div>
  </div>
</div></section>
<section class="section section-alt"><div class="container">
  <h2>How the firm behaves.</h2>
  <div class="grid-2 panels">
    <div class="panel"><h3>Operators first</h3><p>Every engagement opens with an operator's evaluation of the business, never a demo. We speak your language — missed calls, month-end close, speed-to-lead — never the AI industry's. We install nothing we would not run in our own company.</p></div>
    <div class="panel"><h3>Done means done</h3><p>We own evaluation, design, configuration, setup, training, management, and reporting. Nothing counts as installed until your staff can run it. One accountable party, one number to call.</p></div>
    <div class="panel"><h3>People do the human work</h3><p>Every agent is designed around a real worker in a real role. We measure work completed and hours returned — and what those hours went to. We sell growth without hiring, not headcount cuts.</p></div>
    <div class="panel"><h3>Prove it</h3><p>Results in your own KPIs. No figure we have not measured; targets are labelled. Agents disclose that they are agents.</p></div>
    <div class="panel"><h3>Calm</h3><p>Plain words, short sentences, no hype. We tell you what an agent cannot do. Nothing sounds urgent unless it is.</p></div>
  </div>
</div></section>
<section class="section"><div class="container grid-2 gap-lg">
  <div><h2>The AI Native way.</h2><p>Every function that can be delegated to an agent has been. People do the work only people can do. A business that operates this way runs as if it were born AI Native — and that is what a client becomes: an AI Native company.</p><p class="more"><a href="ai-native-company.html">AI Native Company</a></p></div>
  <div><h2>How to say it.</h2><p>A-I Native. The letters, then the word. Two words, capital A, capital I, capital N. The address is ainative.ai.</p></div>
</div></section>
{cta_panel(rel)}'''
    page("about.html", "About AI Native — operators, not vendors", "AI Native is the AI workforce firm, founded by Mark Rukavina and Steve Krell, operators with 35 years building companies in all four categories it serves.", body)


def build_company():
    rel = ""
    body = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">AI Native Company</span><h1>What a client becomes.</h1><p class="lead">A business that has completed the Install and runs on Management operates the AI Native way — agents doing the manual work, people doing the human work. It is an AI Native company, and it may say so.</p></div></section>
<section class="section"><div class="container grid-2 gap-lg">
  <div><h2>The badge.</h2><p>An AI Native company may display the AI Native Company badge on its website and in its materials while Management is active. Its customers see a firm that has put a complete AI workforce behind the counter — and one that tells them so, because every agent identifies itself in its first sentence.</p></div>
  <div><h2>The endorsement.</h2><p>Every agent we install wears our badge and carries the line “powered by AI Native.” It is on the chat widget, in the agent's email signature, and in its voice greeting. Our name is on the work, which is why we manage it.</p></div>
</div></section>
{cta_panel(rel, "Become AI Native.", "The Evaluation is where it starts.")}'''
    page("ai-native-company.html", "AI Native Company — what a client becomes | AI Native", "A business that completes the Install and runs on Management is an AI Native company, and may display the AI Native Company badge.", body)


def build_agents():
    rel = ""
    body = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">Our agents</span><h1>How our agents identify themselves.</h1><p class="lead">If you have spoken with an agent that said “powered by AI Native,” this page is for you.</p></div></section>
<section class="section"><div class="container grid-2 gap-lg">
  <div>
    <h2>What we promise the people our agents talk to.</h2>
    <ul class="dots">
      <li>An AI Native agent says it is an AI agent in its first sentence, every conversation, in chat and by voice. It never pretends to be a person.</li>
      <li>Ask for a person and you get one. Say “person” in chat, or ask on the phone, and the agent steps back.</li>
      <li>It answers from the business's own information. When it is not sure, it says so and hands off.</li>
      <li>It confirms what it did — the booking, the order, the reply — in one plain sentence.</li>
      <li>It does not sell you things you did not ask about, and it does not keep you waiting to make a point.</li>
    </ul>
  </div>
  <div>
    <h2>What it sounds like.</h2>
    <blockquote class="agent-quote"><p>“Thanks for calling Desert Air. This is the Desert Air service agent — I'm an AI agent, powered by AI Native. How can I help?”</p><cite>an example greeting; the business name is illustrative</cite></blockquote>
    <h2>Questions or concerns</h2>
    <p>If an agent that says “powered by AI Native” did not behave this way, tell us{" at <a href=\"mailto:" + CFG["CONTACT_EMAIL"] + "\">" + CFG["CONTACT_EMAIL"] + "</a>" if CFG["CONTACT_EMAIL"] else ""}. A person reads every message.</p>
  </div>
</div></section>'''
    page("agents.html", "How our agents identify themselves | AI Native", "Every AI Native agent says it is an AI agent in its first sentence, hands to a person when asked, and answers only from the business's own information.", body)


def build_evaluation():
    rel = ""
    alt = []
    if CFG["CALENDAR_URL"]: alt.append(f'<a class="btn btn-secondary" href="{CFG["CALENDAR_URL"]}">Pick a time now</a>')
    if CFG["CONTACT_PHONE"]: alt.append(f'<a class="btn btn-secondary" href="tel:{CFG["CONTACT_PHONE"].replace(" ", "")}">Call {CFG["CONTACT_PHONE"]}</a>')
    if CFG["CONTACT_EMAIL"]: alt.append(f'<a class="btn btn-secondary" href="mailto:{CFG["CONTACT_EMAIL"]}?subject=Evaluation">Email {CFG["CONTACT_EMAIL"]}</a>')
    alt_html = f'<div class="alt-paths"><p class="eyebrow">Or</p>{"".join(alt)}</div>' if alt else ""
    body = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">Book the Evaluation</span><h1>Two hours with your leadership. The map, the number, and the timeline, in writing.</h1><p class="lead">Tell us who you are and where the day goes. A person replies within {CFG["REPLY_WITHIN"]} to set the time.</p></div></section>
<section class="section"><div class="container eval-grid">
  <div class="eval-form-col">{eval_form(rel)}{alt_html}</div>
  <aside class="eval-aside">
    <h2>What happens next</h2>
    <ol class="mini-steps">
      <li><strong>We reply.</strong> A person — not a form autoresponder — confirms a time and asks who should be in the room.</li>
      <li><strong>The Evaluation.</strong> Department by department, we map the work done by hand today and show you what an agent takes, what it is tied into, and who checks it.</li>
      <li><strong>The plan.</strong> You leave with the workforce we would install, the number, and the timeline — in writing. The Install begins only when your leadership signs.</li>
    </ol>
    <h2>Who should attend</h2>
    <p>The owner, and the people who carry the manual work: the office manager, the controller or bookkeeper, whoever runs sales and service.</p>
    <h2>What we will not do</h2>
    <p>Add you to a newsletter, run a drip sequence, or hand your details to anyone else. We are a firm; we will call you back.</p>
  </aside>
</div></section>'''
    page("evaluation.html", "Book the Evaluation | AI Native", "Book the AI Native Evaluation: two hours with your leadership, department by department. You leave with the map, the number, and the timeline in writing.", body)


def build_legal():
    rel = ""; today = "September 13, 2026"
    privacy = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">Privacy</span><h1>Privacy policy.</h1><p class="lead">Last updated {today}. Written in plain words; reviewed by counsel before publication.</p></div></section>
<section class="section"><div class="container prose">
  <h2>What we collect</h2><p>When you book an Evaluation we collect what you type into the form: your name, company, work email, phone if you give it, the kind and size of your business, and what you tell us about where the day goes. We use it to reply to you and to prepare for the Evaluation. We do not sell it, rent it, or share it with anyone outside the firm and the service that delivers the form to us.</p>
  <h2>What the website itself collects</h2><p>This site sets no advertising cookies. It stores one preference in your browser — your colour theme — and nothing else. Fonts are loaded from Google Fonts, which receives the request for the font files{"; analytics, if any, are described here" if CFG["ANALYTICS_SNIPPET"] else ""}.</p>
  <h2>Email and calls</h2><p>If you write to us or call, we keep the correspondence so we can answer it. We do not add you to a newsletter unless you ask to join one.</p>
  <h2>Our agents</h2><p>AI Native agents that work inside a client's business are governed by that client's privacy policy and by the Install agreement between the client and AI Native. Every agent identifies itself as an AI agent in its first sentence.</p>
  <h2>Your choices</h2><p>Ask us what we hold about you, ask us to correct it, or ask us to delete it{" by writing to <a href=\"mailto:" + CFG["CONTACT_EMAIL"] + "\">" + CFG["CONTACT_EMAIL"] + "</a>" if CFG["CONTACT_EMAIL"] else ""}. We answer within {CFG["REPLY_WITHIN"]}.</p>
  <h2>Changes</h2><p>If this policy changes, the date at the top changes with it.</p>
</div></section>'''
    page("privacy.html", "Privacy policy | AI Native", "How AI Native handles what you share on this site — in plain words.", privacy)
    terms = f'''
<section class="page-hero"><div class="container"><span class="eyebrow">Terms</span><h1>Terms of use.</h1><p class="lead">Last updated {today}. For this website; the Install agreement governs the work. Reviewed by counsel before publication.</p></div></section>
<section class="section"><div class="container prose">
  <h2>The site</h2><p>ainative.ai is published by AI Native for information about the firm and to book the Evaluation. You may read it, link to it, and quote from it with attribution. You may not copy its design, its badge, or its logotype, or present its content as your own.</p>
  <h2>Trademarks</h2><p>AI Native and the badge are trademarks of AI Native. The lowercase industry term “ai-native” is not.</p>
  <h2>Figures</h2><p>Figures on this site are measured results or are labelled as targets for illustration. They are not a promise of results for your business; the Evaluation is where your numbers begin.</p>
  <h2>The Evaluation</h2><p>Booking an Evaluation creates no obligation on either side. The Install and Management are governed by the agreement your leadership signs.</p>
  <h2>Liability</h2><p>The site is provided as is. To the extent the law allows, AI Native is not liable for loss arising from reliance on the site's content.</p>
  <h2>Law</h2><p>These terms are governed by the laws of the State of Arizona, United States. <!-- COUNSEL: confirm governing law and venue --></p>
</div></section>'''
    page("terms.html", "Terms of use | AI Native", "Terms of use for ainative.ai.", terms)
    nf = '''<section class="page-hero"><div class="container"><span class="eyebrow">404</span><h1>That page is not here.</h1><p class="lead">The address may have changed. Everything the site has is in the menu, and the Evaluation is one click away.</p><p class="hero-actions"><a class="btn btn-primary" href="index.html">Home</a> <a class="btn btn-secondary" href="evaluation.html">Book the Evaluation</a></p></div></section>'''
    page("404.html", "Page not found | AI Native", "Page not found.", nf)


def build_static():
    pages = ["", "how-it-works.html", "workforce.html", "businesses/", "businesses/b2b-service.html", "businesses/b2b-product.html", "businesses/b2c-service.html", "businesses/b2c-product.html", "report.html", "answers.html", "about.html", "ai-native-company.html", "agents.html", "evaluation.html", "privacy.html", "terms.html"]
    d = datetime.date.today().isoformat()
    open(f"{OUT}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f'  <url><loc>{CFG["SITE_URL"]}/{p}</loc><lastmod>{d}</lastmod></url>\n' for p in pages) + "</urlset>\n")
    open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {CFG['SITE_URL']}/sitemap.xml\n")
    json.dump({"name": "AI Native", "short_name": "AI Native", "start_url": "/", "display": "standalone", "background_color": "#1E1F22", "theme_color": "#1E1F22", "icons": [{"src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "assets/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, open(f"{OUT}/site.webmanifest", "w"), indent=1)
    entity = {"@context": "https://schema.org", "@type": "Organization", "name": "AI Native", "url": CFG["SITE_URL"], "logo": f'{CFG["SITE_URL"]}/assets/og-image.png',
              "description": "AI Native is the AI workforce firm: it designs, installs, trains, and manages a complete AI agent workforce for every worker in every department of a U.S. small or medium-sized business, done for you, and reports the results.",
              "founder": [{"@type": "Person", "name": "Mark Rukavina"}, {"@type": "Person", "name": "Steve Krell"}], "areaServed": "US", "slogan": "Your business, AI Native."}
    open(f"{OUT}/entity.jsonld", "w").write(json.dumps(entity, indent=1))


def build_css():
    css = TOKENS + r'''
/* ============ ainative.ai — site styles (built on the AI Native tokens) ============ */
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--an-bg);color:var(--an-text);font-family:var(--an-font-sans);font-size:1rem;line-height:1.6;-webkit-font-smoothing:antialiased}
img,svg{display:block;max-width:100%}
a{color:var(--an-link);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:.15em}
h1,h2,h3{margin:0;font-weight:700;line-height:1.15;letter-spacing:-.01em;text-wrap:balance}
h1{font-size:clamp(2.5rem,6vw,4.75rem);letter-spacing:-.02em;line-height:1.05}
h2{font-size:clamp(1.75rem,3.2vw,2.375rem)}
h3{font-size:1.25rem;letter-spacing:-.005em}
p{margin:0 0 1em}
.container{width:100%;max-width:1264px;margin:0 auto;padding:0 32px}
@media (max-width:899px){.container{padding:0 24px}}
@media (max-width:599px){.container{padding:0 20px}}
.skip{position:absolute;left:-999px;top:8px;background:var(--an-accent);color:var(--an-on-accent);padding:8px 12px;border-radius:8px;z-index:100}
.skip:focus{left:8px}
:focus-visible{outline:2px solid var(--an-focus);outline-offset:2px}
[id]{scroll-margin-top:96px}

/* header — sticky, the CTA always on screen */
.site-header{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--an-bg) 92%,transparent);backdrop-filter:saturate(1.2) blur(10px);-webkit-backdrop-filter:saturate(1.2) blur(10px);border-bottom:1px solid var(--an-border)}
.header-row{display:flex;align-items:center;gap:24px;height:80px}
@media (max-width:1023px){.header-row{height:64px}}
.brand{color:var(--an-text);flex:0 0 auto}
.brand svg{height:26px;width:auto}
@media (max-width:1023px){.brand svg{height:22px}}
.site-nav{flex:1 1 auto}
.site-nav ul{list-style:none;margin:0;padding:0;display:flex;gap:4px;align-items:center}
.site-nav a,.nav-sub-toggle{display:inline-flex;align-items:center;gap:6px;padding:10px 12px;border-radius:8px;color:var(--an-text-secondary);font-weight:500;font-size:.9375rem;background:none;border:0;font:inherit;font-weight:500;cursor:pointer}
.site-nav a:hover,.nav-sub-toggle:hover{color:var(--an-text);background:var(--an-sunken);text-decoration:none}
.site-nav a[aria-current="page"]{color:var(--an-text);box-shadow:inset 0 -2px 0 var(--an-accent);border-radius:8px 8px 0 0}
.has-sub{position:relative}
.sub{position:absolute;top:100%;left:0;min-width:220px;background:var(--an-surface);border:1px solid var(--an-border);border-radius:12px;padding:8px;box-shadow:var(--an-shadow-raised);display:none;flex-direction:column;gap:2px}
.has-sub:hover .sub,.has-sub:focus-within .sub,.has-sub[data-open="true"] .sub{display:flex}
.sub a{width:100%;padding:10px 12px}
.nav-mobile-cta{display:none}
.header-actions{display:flex;align-items:center;gap:12px;margin-left:auto}
.cta .cta-short{display:none}
.menu-toggle{display:none;width:44px;height:44px;border:1px solid var(--an-border-strong);border-radius:8px;background:none;cursor:pointer;flex-direction:column;justify-content:center;align-items:center;gap:5px}
.menu-toggle span{display:block;width:20px;height:2px;background:var(--an-text);border-radius:2px;transition:transform var(--an-duration-base) var(--an-ease-standard),opacity var(--an-duration-base)}
.menu-toggle[aria-expanded="true"] span:nth-child(1){transform:translateY(7px) rotate(45deg)}
.menu-toggle[aria-expanded="true"] span:nth-child(2){opacity:0}
.menu-toggle[aria-expanded="true"] span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
@media (max-width:1023px){
  .menu-toggle{display:flex}
  .cta .cta-long{display:none}.cta .cta-short{display:inline}
  .site-nav{display:none;position:fixed;left:0;right:0;top:64px;bottom:0;background:var(--an-bg);border-top:1px solid var(--an-border);overflow:auto;padding:16px 20px 32px;z-index:49}
  .site-nav[data-open="true"]{display:block}
  .site-nav ul{flex-direction:column;align-items:stretch;gap:0}
  .site-nav li{border-bottom:1px solid var(--an-border)}
  .site-nav a,.nav-sub-toggle{width:100%;padding:16px 4px;font-size:1.125rem;color:var(--an-text);justify-content:space-between}
  .site-nav a[aria-current="page"]{box-shadow:none;color:var(--an-accent-text)}
  .sub{position:static;display:none;border:0;box-shadow:none;background:none;padding:0 0 8px 16px}
  .has-sub[data-open="true"] .sub{display:flex}
  .has-sub:hover .sub{display:none}.has-sub[data-open="true"]:hover .sub{display:flex}
  .sub a{font-size:1rem;color:var(--an-text-secondary)}
  .nav-mobile-cta{display:block;padding-top:20px}
  .nav-mobile-cta .btn{width:100%;justify-content:center}
  body[data-menu-open="true"]{overflow:hidden}
}

/* buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:40px;padding:0 18px;border-radius:8px;font-weight:600;font-size:.9375rem;border:1.5px solid transparent;white-space:nowrap;transition:background var(--an-duration-fast) var(--an-ease-standard),color var(--an-duration-fast)}
.btn:hover{text-decoration:none}
.btn-lg{height:48px;padding:0 22px;font-size:1rem}
.btn-primary{background:var(--an-accent);color:var(--an-on-accent)}
.btn-primary:hover{background:var(--an-accent-hover)}
.btn-secondary{background:none;color:var(--an-text);border-color:var(--an-border-strong)}
.btn-secondary:hover{background:var(--an-sunken)}
.btn-tertiary{background:none;color:var(--an-link);padding:0 8px;text-decoration:underline;text-underline-offset:.2em}
.btn-on-dark{background:var(--an-accent);color:#1E1F22}
.link-on-dark{color:inherit;text-decoration:underline;text-underline-offset:.2em;opacity:.85}

/* the band device */
.has-band{position:relative;overflow:hidden}
.has-band::after{content:"";position:absolute;left:0;right:0;bottom:0;height:8%;min-height:8px;max-height:32px;background:var(--an-accent)}

/* layout primitives */
.section{padding:96px 0}
.section-alt{background:var(--an-sunken)}
@media (max-width:899px){.section{padding:64px 0}}
@media (max-width:599px){.section{padding:48px 0}}
.section h2{margin-bottom:12px}
.section-lead{font-size:1.25rem;line-height:1.5;color:var(--an-text-secondary);max-width:42em;margin-bottom:32px}
.lead{font-size:clamp(1.125rem,1.6vw,1.375rem);line-height:1.5;color:var(--an-text-secondary);max-width:38em}
.grid-2,.grid-3,.grid-4{display:grid;gap:24px}
.grid-2{grid-template-columns:repeat(2,1fr)}.grid-3{grid-template-columns:repeat(3,1fr)}.grid-4{grid-template-columns:repeat(4,1fr)}
.gap-lg{gap:48px}
@media (max-width:899px){.grid-4{grid-template-columns:repeat(2,1fr)}.grid-3{grid-template-columns:1fr}.gap-lg{gap:32px}}
@media (max-width:599px){.grid-2,.grid-4{grid-template-columns:1fr}}
.eyebrow{display:block;font-size:.875rem;font-weight:500;color:var(--an-accent-text);margin-bottom:8px}
.note{font-size:.875rem;color:var(--an-text-tertiary);margin-top:16px}
.more{margin-top:20px;font-weight:500}
.promise{font-weight:600;font-size:1.125rem;margin-top:28px}
.dots{list-style:none;margin:0;padding:0}
.dots li{position:relative;padding-left:22px;margin-bottom:10px}
.dots li::before{content:"";position:absolute;left:0;top:.65em;width:8px;height:8px;border-radius:50%;background:var(--an-accent)}
.grid-2.dots{gap:8px 32px}

/* hero */
.hero{padding:96px 0 80px}
@media (max-width:899px){.hero{padding:56px 0 48px}}
.hero-grid{display:grid;grid-template-columns:7fr 5fr;gap:48px;align-items:center}
@media (max-width:899px){.hero-grid{grid-template-columns:1fr;gap:40px}}
.hero-copy .lead{margin:24px 0 32px}
.hero-actions{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center}
.results{background:var(--an-surface);border:1px solid var(--an-border);border-radius:16px;padding:28px 28px 44px}
.results-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px;font-weight:600;margin-bottom:8px}
.results-note{font-size:.75rem;font-weight:400;color:var(--an-text-tertiary)}
.results-list{margin:0}
.results-list div{display:flex;justify-content:space-between;gap:12px;padding:14px 0;border-top:1px solid var(--an-border)}
.results-list dt{color:var(--an-text-secondary)}
.results-list dd{margin:0;font-family:var(--an-font-mono);font-weight:500;font-variant-numeric:tabular-nums}

/* page hero */
.page-hero{padding:80px 0 40px}
@media (max-width:899px){.page-hero{padding:48px 0 24px}}
.page-hero h1{max-width:20em;margin-bottom:20px}

/* owners */
.owner{display:block;padding:24px;border-radius:12px;border:1px solid var(--an-border);background:var(--an-surface);color:var(--an-text)}
.owner:hover{text-decoration:none;border-color:var(--an-border-strong)}
.owner-line{display:block;font-size:1.25rem;font-weight:600;line-height:1.3;letter-spacing:-.005em}

/* panels */
.panel{background:var(--an-sunken);border-radius:12px;padding:28px}
.section-alt .panel{background:var(--an-surface);border:1px solid var(--an-border)}
.panel h3{margin-bottom:10px}
.panel p{margin:0;color:var(--an-text-secondary)}
.panel-ink{background:var(--an-text);color:var(--an-bg);padding-bottom:44px}
.panel-ink p,.panel-ink h3{color:inherit}
.panel-badge{width:30px;margin-bottom:12px;color:var(--an-bg)}
.panels{align-items:stretch}

/* roster table */
.table-wrap{overflow:auto;border:1px solid var(--an-border);border-radius:12px;background:var(--an-surface)}
.roster{width:100%;border-collapse:collapse;font-size:.9375rem}
.roster th,.roster td{text-align:left;padding:14px 20px;border-top:1px solid var(--an-border);vertical-align:top}
.roster thead th{border-top:0;font-size:.8125rem;font-weight:500;color:var(--an-text-tertiary)}
.roster tbody th{font-weight:600;white-space:nowrap}
.roster td:nth-child(2){color:var(--an-text-secondary)}
.agent-chip{display:inline-flex;align-items:center;gap:8px;font-weight:500;white-space:nowrap}
.agent-badge{display:inline-block;width:14px;color:var(--an-text)}
.table-wrap .note{padding:0 20px 16px;margin-top:12px}
@media (max-width:699px){
  .roster thead{display:none}
  .roster tr{display:block;padding:12px 16px;border-top:1px solid var(--an-border)}
  .roster th,.roster td{display:block;padding:4px 0;border:0}
  .roster td::before{content:attr(data-label);display:block;font-size:.75rem;color:var(--an-text-tertiary)}
  .roster tbody th{white-space:normal}
}

/* steps */
.steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,1fr);gap:24px}
@media (max-width:899px){.steps{grid-template-columns:repeat(2,1fr)}}
@media (max-width:599px){.steps{grid-template-columns:1fr}}
.step-n{display:block;font-family:var(--an-font-mono);font-size:1.75rem;color:var(--an-accent-text);margin-bottom:12px}
.steps h3{margin-bottom:8px}
.steps p{color:var(--an-text-secondary);margin:0}
.stage-list{display:grid;gap:40px}
.stage{display:grid;grid-template-columns:64px 1fr;gap:24px;padding:32px;background:var(--an-surface);border:1px solid var(--an-border);border-radius:16px}
@media (max-width:599px){.stage{grid-template-columns:1fr;padding:24px}}
.stage h2{margin-bottom:12px}
.stage .step-n{font-size:2.25rem}

/* cards */
.card{display:flex;flex-direction:column;gap:10px;padding:24px;border-radius:12px;border:1px solid var(--an-border);background:var(--an-surface);color:var(--an-text)}
.card:hover{text-decoration:none;border-color:var(--an-border-strong)}
.card p{color:var(--an-text-secondary);margin:0;flex:1}
.card-link{color:var(--an-link);font-weight:500;font-size:.9375rem}
.card-mini h3{font-size:1.125rem}

/* operators */
.operators{display:grid;grid-template-columns:5fr 7fr;gap:48px;align-items:center}
@media (max-width:899px){.operators{grid-template-columns:1fr;gap:32px}}
.operators-photo{aspect-ratio:3/2;border-radius:12px;background:linear-gradient(135deg,var(--an-sunken),var(--an-border))}
.founders{margin-top:24px}
.founder h3{font-size:1.125rem}
.founder-role{color:var(--an-text-tertiary);font-size:.875rem;margin-bottom:6px}

/* KPIs and charts */
.kpis{margin-bottom:32px}
.kpi{display:flex;flex-direction:column;gap:6px;padding:20px;border:1px solid var(--an-border);border-radius:12px;background:var(--an-surface)}
.kpi-label{font-size:.875rem;color:var(--an-text-secondary)}
.kpi-value{font-family:var(--an-font-mono);font-weight:500;font-size:1.75rem;font-variant-numeric:tabular-nums}
.kpi-delta{font-size:.8125rem;color:var(--an-success)}
.kpi-delta.is-target{color:var(--an-text-tertiary)}
.chart{margin:0;padding:24px;border:1px solid var(--an-border);border-radius:12px;background:var(--an-surface)}
.chart figcaption{font-weight:600;margin-bottom:12px}
.chart svg{width:100%;height:auto}
.gridline{stroke:var(--an-border)}
.bar-before{fill:var(--an-color-aluminum)}.bar-after{fill:var(--an-accent)}
.bar-val{font-family:var(--an-font-mono);font-size:12px;fill:var(--an-text-secondary)}.bar-val.is-after{fill:var(--an-text);font-weight:500}
.bar-cat{font-size:12px;fill:var(--an-text-secondary)}
.legend{display:flex;gap:20px;flex-wrap:wrap;font-size:.8125rem;color:var(--an-text-secondary);margin-top:8px;align-items:center}
.legend .sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:middle}
.sw-before{background:var(--an-color-aluminum)}.sw-after{background:var(--an-accent)}
.legend-note{color:var(--an-text-tertiary);margin-left:auto}

/* answers */
.answers{display:grid;gap:12px}
.answers-page{max-width:760px}
.answer{border:1px solid var(--an-border);border-radius:12px;background:var(--an-surface);padding:0 20px}
.answer summary{list-style:none;cursor:pointer;padding:18px 0;display:flex;align-items:center;justify-content:space-between;gap:16px}
.answer summary::-webkit-details-marker{display:none}
.answer summary::after{content:"+";font-family:var(--an-font-mono);color:var(--an-accent-text);font-size:1.25rem;flex:0 0 auto}
.answer[open] summary::after{content:"–"}
.answer summary h3{font-size:1.0625rem}
.answer p{color:var(--an-text-secondary);padding-bottom:18px;margin:0}
.q{font-size:1.25rem;margin:8px 0 12px}

/* agents */
.agent-grid{gap:16px}
.agent-card{padding:24px;border:1px solid var(--an-border);border-radius:12px;background:var(--an-surface)}
.agent-card-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px}
.agent-card-head .agent-badge{width:18px}
.agent-dept{font-size:.8125rem;color:var(--an-text-tertiary)}
.agent-card p{margin:0;color:var(--an-text-secondary)}
.install-list{list-style:none;margin:0;padding:0}
.install-list li{display:grid;gap:4px;padding:12px 0;border-top:1px solid var(--an-border)}
.install-what{color:var(--an-text-secondary)}
.agent-quote{margin:0 0 32px;padding:20px 24px;border-left:3px solid var(--an-accent);background:var(--an-sunken);border-radius:0 12px 12px 0}
.agent-quote p{font-family:var(--an-font-serif);font-size:1.25rem;line-height:1.5;margin:0 0 8px}
.agent-quote cite{font-style:normal;font-size:.8125rem;color:var(--an-text-tertiary)}

/* CTA panel, book panel */
.cta-panel{background:var(--an-text);color:var(--an-bg);padding:72px 0 88px}
.cta-inner{width:100%;max-width:1264px;margin:0 auto;padding:0 32px;display:grid;grid-template-columns:7fr 5fr;gap:32px;align-items:center}
@media (max-width:899px){.cta-inner{grid-template-columns:1fr;padding:0 24px}}
.cta-panel h2{color:inherit;margin-bottom:12px}
.cta-panel p{color:inherit;opacity:.85;max-width:36em;margin:0}
.cta-actions{display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:flex-end}
@media (max-width:899px){.cta-actions{justify-content:flex-start}}
.book-panel{background:var(--an-text);color:var(--an-bg);border-radius:16px;padding:48px 48px 64px;display:grid;grid-template-columns:5fr 7fr;gap:48px}
@media (max-width:899px){.book-panel{grid-template-columns:1fr;padding:32px 24px 48px}}
.book-panel h2{color:inherit}.book-panel p{color:inherit;opacity:.85}

/* forms */
.eval-form .form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:599px){.eval-form .form-grid{grid-template-columns:1fr}}
.field{display:flex;flex-direction:column;gap:6px}
.field-wide{grid-column:1/-1}
.field label{font-size:.875rem;font-weight:500}
.field .opt{font-weight:400;color:var(--an-text-tertiary)}
.field input,.field select,.field textarea{width:100%;font:inherit;font-size:1rem;padding:10px 14px;border-radius:8px;border:1px solid var(--an-border-strong);background:var(--an-surface);color:var(--an-text)}
.field input:focus,.field select:focus,.field textarea:focus{outline:2px solid var(--an-focus);outline-offset:2px;border-color:var(--an-focus)}
.field input[aria-invalid="true"],.field select[aria-invalid="true"]{border-color:var(--an-error)}
.book-panel .field label{color:inherit}
.book-panel .field input,.book-panel .field select,.book-panel .field textarea{background:var(--an-bg);color:var(--an-text);border-color:transparent}
.hp{position:absolute;left:-9999px;opacity:0;height:0;width:0}
.form-actions{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:20px}
.form-note{font-size:.875rem;margin:0;opacity:.8}
.form-status{margin-top:12px;font-weight:500;min-height:1.5em}
.form-status.is-error{color:var(--an-error)}
.eval-grid{display:grid;grid-template-columns:7fr 5fr;gap:48px;align-items:start}
@media (max-width:899px){.eval-grid{grid-template-columns:1fr}}
.eval-aside{position:sticky;top:104px;padding:28px;border:1px solid var(--an-border);border-radius:16px;background:var(--an-surface)}
.eval-aside h2{font-size:1.125rem;margin:0 0 10px}
.eval-aside h2+ol,.eval-aside h2+p{margin-bottom:24px}
.mini-steps{padding-left:20px;margin:0}
.mini-steps li{margin-bottom:10px;color:var(--an-text-secondary)}
.mini-steps strong{color:var(--an-text)}
.alt-paths{margin-top:32px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}

/* prose */
.prose{max-width:720px}
.prose h2{font-size:1.375rem;margin:32px 0 8px}
.prose p{color:var(--an-text-secondary)}

/* footer */
.site-footer{margin-top:96px;border-top:1px solid var(--an-border);background:var(--an-sunken)}
@media (max-width:899px){.site-footer{margin-top:64px}}
.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:32px;padding:56px 0 24px}
@media (max-width:899px){.footer-grid{grid-template-columns:1fr 1fr}}
@media (max-width:599px){.footer-grid{grid-template-columns:1fr;gap:24px}}
.url-lockup{display:block;width:180px;color:var(--an-text)}
.footer-tag{font-weight:500;margin:16px 0 4px}
.footer-support{color:var(--an-text-secondary);font-size:.9375rem;margin:0}
.footer-h{font-size:.875rem;font-weight:600;margin:0 0 12px;color:var(--an-text)}
.site-footer ul{list-style:none;margin:0;padding:0}
.site-footer li{margin-bottom:8px}
.site-footer li a{color:var(--an-text-secondary);font-size:.9375rem}
.footer-legal{border-top:1px solid var(--an-border);padding:20px 0 28px;font-size:.8125rem;color:var(--an-text-tertiary)}
.footer-legal p{margin:0 0 6px}
.footer-legal a{color:var(--an-text-secondary)}
.theme-toggle{background:none;border:0;padding:0;font:inherit;color:var(--an-text-secondary);cursor:pointer;text-decoration:underline;text-underline-offset:.15em}
.site-band{height:12px;background:var(--an-accent)}

@media print{.site-header,.site-footer .theme-toggle,.menu-toggle{display:none}.section{padding:32px 0}}
'''
    open(f"{OUT}/css/site.css", "w").write(css)


def build_js():
    js = r'''/* ainative.ai — navigation, theme, evaluation form */
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
'''
    open(f"{OUT}/js/site.js", "w").write(js)


def build_readme():
    open(f"{OUT}/README-GO-LIVE.md", "w").write(f'''# ainative.ai — go-live notes

This folder is the complete static site. Upload it as-is to the root of any static host (Netlify, Vercel, Cloudflare Pages, GitHub Pages, S3 + CloudFront, or the web root of any server). No build step, no server code, no database. HTTPS is automatic on the hosts named.

## Before going live — fill the configuration
The pages were generated with these values (see `build_site.py`, `CFG`). Set them and regenerate, or edit the HTML directly:

| Key | What it does | Current |
|---|---|---|
| FORM_ENDPOINT | Where the Evaluation form posts (Formspree, Basin, Netlify Forms, or your CRM's form endpoint). Empty = the form opens the visitor's email app addressed to CONTACT_EMAIL. | {CFG["FORM_ENDPOINT"] or "not set"} |
| CONTACT_EMAIL | Shown in the footer, on the agents page, and used by the mailto fallback | {CFG["CONTACT_EMAIL"] or "not set"} |
| CONTACT_PHONE | Shown in the footer and as a button on the Evaluation page | {CFG["CONTACT_PHONE"] or "not set"} |
| CALENDAR_URL | "Pick a time now" button on the Evaluation page (Cal.com, Calendly, HubSpot Meetings, Google appointment page) | {CFG["CALENDAR_URL"] or "not set"} |
| ANALYTICS_SNIPPET | Optional analytics tag (Plausible, Fathom, GA4) | {"set" if CFG["ANALYTICS_SNIPPET"] else "not set"} |
| AGENT_WIDGET_SNIPPET | The AI Native service agent widget for this site, once it exists | {"set" if CFG["AGENT_WIDGET_SNIPPET"] else "not set"} |
| REPLY_WITHIN | The reply commitment shown next to the form | {CFG["REPLY_WITHIN"]} |

Also: the founders' biographies and portrait photographs on `about.html` (marked in HTML comments); the workplace photographs in the "Operators, not vendors" sections (currently a neutral field); counsel's review of `privacy.html`, `terms.html`, and the "What about our data?" answer.

## Structure
- `index.html` and the pages listed in `sitemap.xml`; `businesses/` holds the four category pages.
- `css/site.css` — the brand tokens plus the site styles; `js/site.js` — menu, theme, form.
- `assets/` — logotype and badge as inline-ready SVG, favicons, touch icons, the Open Graph image.
- `entity.jsonld` — the canonical organisation description; paste it into a `<script type="application/ld+json">` on the home page or serve as is.

## Fonts
Loaded from Google Fonts (Atkinson Hyperlegible Next, Atkinson Hyperlegible Mono, Source Serif 4). To self-host, copy `05-typography/fonts` and `fonts.css` from the brand asset package into `assets/fonts/` and replace the Google Fonts link in each page's head.

## Responsive behaviour
Breakpoints 600 / 900 / 1024 / 1264. The header is sticky; the "Book the Evaluation" button is in it on every page at every width (it shortens to "Book" under 1024 px). Dark mode is native; light follows the visitor's system preference, and the footer toggle overrides it.
''')


if __name__ == "__main__":
    build_css(); build_js(); build_static(); build_home(); build_how(); build_workforce()
    for k in CATS: build_category(k)
    build_businesses_index(); build_report(); build_answers(); build_about(); build_company(); build_agents(); build_evaluation(); build_legal(); build_static(); build_readme()
    print("site built:", len([f for r, d, fs in os.walk(OUT) for f in fs]), "files")
