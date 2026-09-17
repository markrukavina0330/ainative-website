# The AI Native service agent — front-end contract for the backend

`js/agent.js` renders the launcher, the panel (floating; full-screen under 600 px), and the inline showcase on the home page (`#agent-inline`). One conversation is shared by both and persists for the session in `sessionStorage`.

## Switching to the live agent
Set `AGENT_MODE = "live"` and `AGENT_ENDPOINT = "https://…/agent"` in `build_site.py` (or edit `window.AI_NATIVE_SITE` in each page) and regenerate.

## Request (POST, JSON)
```json
{ "session_id": "s…", "message": "What would you install at an HVAC company?",
  "page": { "url": "https://ainative.ai/", "title": "AI Native™ — …" },
  "history": [ { "who": "user", "text": "…" }, { "who": "agent", "text": "…" } ] }
```

## Response (JSON) — an ordered list of messages
```json
{ "messages": [
  { "type": "text",  "text": "For a business like that we usually install …" },
  { "type": "chips", "options": ["Book the Evaluation", "How does handoff work?"] },
  { "type": "card",  "kind": "link",    "title": "B2C service", "text": "Where the day goes …", "href": "businesses/b2c-service.html", "cta": "See the map" },
  { "type": "card",  "kind": "book",    "title": "Book the Evaluation", "text": "Three fields." },
  { "type": "card",  "kind": "handoff", "title": "A person, not the agent", "text": "Here are the ways to reach a person." }
] }
```
- `text` renders as an agent bubble; `chips` are one-tap replies that send their label; `link` cards open a page; `book` renders the three-field booking form (posts to FORM_ENDPOINT or opens email to FORM_EMAIL); `handoff` renders the call / pick-a-time / email actions from the site configuration.
- The backend owns the persona: the first sentence of every new session must be the disclosure ("I'm an AI agent, powered by AI Native"); three sentences a turn; one question; hand off on "person", on uncertainty, and on listed topics. The front end shows the disclosure line in its footer regardless.
- Streaming is not required; if added later, send the final message list at the end of the stream.
- Errors (non-2xx) make the front end show a handoff card.
