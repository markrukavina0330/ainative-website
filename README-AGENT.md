# The AI Native Front Desk agent on this site

The agent is the Front Desk application at https://agent.ainative.ai, which has its own repository. This site
carries three things and nothing else:

1. **One script line** at the end of every page:
   `<script src="https://agent.ainative.ai/widget.js" defer></script>`
2. **`<div data-ainative-inline></div>`** where the agent sits inside a page: the home page's "Our own agent"
   section and the top of the Evaluation page. Every other page shows the round launcher at the bottom right.
3. **`data-ainative-open`** on any link or button that opens the agent: the header's "Book the Evaluation" on every
   page (it keeps its link to evaluation.html, so it still works if the script does not load) and the "Ask our agent"
   links.

The agent's words, colours, privacy line, and contact address come from the application (`/api/settings`), so
changing them needs no change here. Three rules at the end of `css/site.css` hold the inline panel's space so nothing
on the page moves when the script arrives. If the agent is unavailable, its panel shows evaluation@ainative.ai instead.

The Calendly link and the form stay on the Evaluation page for two weeks after launch, then come off.
