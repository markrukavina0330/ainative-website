# The AI Native Front Desk agent on this site

The agent is the Front Desk application at https://agent.ainative.ai, which has its own repository. This site
carries three things and nothing else:

1. **One script line** at the end of every page:
   `<script src="https://agent.ainative.ai/widget.js" defer></script>`
2. **`data-ainative-inline`** on the element the agent sits inside: `<div data-ainative-inline></div>` in the home
   page's "Our own agent" section, and on the Evaluation page the Front Desk container itself,
   `<div id="front-desk-agent" class="front-desk" data-front-desk data-ainative-inline>` (v1.12). Put the attribute on
   the container, not on a child div: js/site.js shows the written fallback (evaluation@ainative.ai) only if nothing
   but the fallback is inside the container after eight seconds. Every other page shows the round launcher at the
   bottom right.
3. **`data-ainative-open`** on any link or button that opens the agent: the header's "Book the Evaluation" on every
   page (it keeps its link to evaluation.html, so it still works if the script does not load) and the "Ask our agent"
   links.

The agent's words, colours, privacy line, and contact address come from the application (`/api/settings`), so
changing them needs no change here. Three rules at the end of `css/site.css` hold the inline panel's space so nothing
on the page moves when the script arrives. If the agent is unavailable, its panel shows evaluation@ainative.ai instead.

The Calendly link and the forms came off in v1.12 (September 28, 2026); the agent is the booking path, and the
Evaluation page names one address, evaluation@ainative.ai.
