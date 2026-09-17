# ainative.ai — go-live notes

This folder is the complete static site. Upload it as-is to the root of any static host (Netlify, Vercel, Cloudflare Pages, GitHub Pages, S3 + CloudFront, or the web root of any server). No build step, no server code, no database. HTTPS is automatic on the hosts named.

## Configuration (build_site.py, CFG) — current values
| Key | Current | Note |
|---|---|---|
| FORM_ENDPOINT | not set | When set (Formspree, Basin, Netlify Forms, the CRM), the form and the agent's booking card POST here. Empty = the visitor's email app opens, addressed to FORM_EMAIL. |
| FORM_EMAIL | evaluation@ainative.ai | Evaluation requests |
| CONTACT_EMAIL | sales@ainative.ai | Footer, agents page, the agent's handoff card — confirmed |
| CONTACT_PHONE | 602-680-8011 | Footer, Evaluation page, the agent's handoff card |
| CALENDAR_URL | https://calendly.com/ainative/evaluation | PLACEHOLDER — replace with the real Calendly event link before go-live |
| GA4_ID | G-XXXXXXXXXX | Google Analytics 4 measurement ID — PLACEHOLDER until you paste the real G- id (Admin → Data streams → Web) |
| AGENT_MODE / AGENT_ENDPOINT | demo / not set | "demo" answers from the site's own content in the browser; "live" POSTs to the endpoint — see README-AGENT.md |
| REPLY_WITHIN | one business day | Shown beside the form |

Still to supply: the real GA4 measurement ID; the real Calendly event link; the photograph of the senior leadership team in a client workplace (replace `assets/people/founders-workplace.jpg`, currently marked FPO, keeping the file name); counsel's review of privacy.html, terms.html, and the data answer; the agent backend.

## Structure
- `index.html` and the pages in `sitemap.xml`; `businesses/` holds the four category pages.
- `css/site.css` — brand tokens + site + agent styles; `js/site.js` — menu, theme, form; `js/agent.js` — the AI Native service agent front end.
- `assets/` — logotype and badge SVG, favicons, touch icons, Open Graph image, the leadership-team photograph (FPO).
- `entity.jsonld` — the canonical organisation description (also embedded in index.html).

## Fonts
Google Fonts (Atkinson Hyperlegible Next, Atkinson Hyperlegible Mono, Source Serif 4). To self-host, copy the font package from the brand assets into `assets/fonts/` and swap the link in each page's head.

## Responsive behaviour
Breakpoints 600 / 900 / 1024 / 1264 px. The header is sticky with "Book the Evaluation" on every page at every width (shortens to "Book" under 1024 px). Dark mode is native; light follows the visitor's system preference; the footer toggle overrides it. The agent is a floating launcher on every page, a full-screen sheet on phones, and is docked inline on the home page.
