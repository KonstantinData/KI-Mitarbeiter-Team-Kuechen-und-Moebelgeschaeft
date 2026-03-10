# AI Employee Team for Kitchen and Furniture Stores

🇩🇪 [Deutsch](README.md) | 🇬🇧 [English](README.en.md)

---

A complete system of AI-powered virtual employees that helps kitchen and furniture stores handle customer inquiries 24/7 — from first chat contact to appointment booking.

---

## What is this?

This project is the technical foundation for a team of AI agents that work in the background like real employees: They greet visitors on the website, conduct consultations, qualify leads, book appointments, and coordinate follow-ups — automatically, 24/7, in natural language.

The system is designed as a **ready-to-use platform**: A kitchen studio purchases access, sets up their studio, and the AI employees go straight to work. Multiple studios can use the system simultaneously without affecting each other. All employees can work **in parallel** with different visitors at the same time.

---

## How does the integration work?

The system is **not a replacement** for the existing website — it integrates invisibly:

```html
<!-- A single line in the existing website -->
<script
  src="https://widget.mein-kuechenexperte.de/loader.iife.js"
  data-studio="mein-kuechenexperte"
></script>
```

That's it. The chat button appears, and the AI employees are ready to go.

---

## The AI Employees (planned)

A single chat window for the visitor — in the background, the appropriate employee automatically takes over depending on the conversation phase.

| Name | Task | When active |
| ---- | ---- | ----------- |
| **Lisa** | First contact, greeting, lead capture | As soon as someone visits the website |
| **Max** | Consultation, planning, offers | When the customer has specific questions |
| **Anna** | Order processing, documents | After purchase |
| **Tom** | Delivery, installation, coordination | Shortly before delivery date |
| **Sara** | Quality assurance, customer retention | After installation |

> **Current status:** The foundation is complete. Individual agents will be added in the next development steps.

---

## What does it look like for the end customer?

A visitor to `www.mein-kuechenexperte.de` sees a chat button in the corner. They click, write their question — and Lisa responds immediately. The conversation feels like a real conversation. In the background, the system captures all important information, evaluates the prospect, and plans the next step (e.g., a consultation appointment).

The kitchen studio sees everything in an admin dashboard at `app.mein-kuechenexperte.de`: which leads have come in, what was discussed, which appointments are upcoming.

---

## Where does what run?

| Component | URL | Platform |
| --------- | --- | -------- |
| **Chat Widget** (for website visitors) | `widget.mein-kuechenexperte.de` | Cloudflare Pages |
| **Admin Dashboard** (for studio operators) | `app.mein-kuechenexperte.de` | Cloudflare Pages |
| **Backend / AI** (invisible in background) | `api.mein-kuechenexperte.de` | Hetzner Cloud (EU) |
| **Main website** (unchanged) | `www.mein-kuechenexperte.de` | existing |

---

## What is currently complete?

### Infrastructure & Backend

- Complete **database schema** (prospects, conversations, appointments, knowledge base, audit trail)
- **API server** with all necessary endpoints (authentication, chat, studios, leads, appointments, etc.)
- **Real-time chat** via WebSocket — messages are transmitted in milliseconds
- **Knowledge search**: The system can semantically search a studio's product database and pass relevant information to the AI
- **Memory system**: Each agent remembers what was discussed in previous conversations with a customer
- **Multi-studio operation**: Any number of studios can use the system in parallel — completely separated from each other

### AI Core

- Pre-built **agent structure**: Each new agent follows the same 7-step process (load context → understand request → retrieve knowledge → use tools → respond → save)
- Connection to **Anthropic Claude** (state-of-the-art language model technology) for natural conversations and complex reasoning
- **Tool system**: Agents can independently perform actions (check appointments, send emails, save data)
- **Template for new agents**: A new employee (e.g., Lisa) can be quickly created by copying and adapting a template

### Frontend

- **Chat widget**: A `<script>` tag is enough to integrate into any existing website
- **Admin dashboard**: Web interface for the kitchen studio with login, overviews, and navigation
- Both frontends **live on Cloudflare Pages** with automatic SSL and custom domains

### Deployment & Operations

- **Backend** runs on a European server (Hetzner, GDPR-compliant)
- **Frontends** via Cloudflare Pages — fast, worldwide, fail-safe
- Automatic deployments: Every code push triggers a new build
- Configuration and deployment scripts for quick setup

---

## Project Structure (simplified)

```text
KI-Mitarbeiter-Team/
│
├── src/
│   ├── core/          # Shared core of all agents (LLM, memory, knowledge, tools)
│   ├── agents/        # Individual AI employees (Lisa, Max, Anna, Tom, Sara)
│   ├── api/           # API server (endpoints, WebSocket, authentication)
│   └── db/            # Database models and migrations
│
├── frontends/
│   ├── widget/        # Chat widget → widget.mein-kuechenexperte.de
│   └── dashboard/     # Admin dashboard → app.mein-kuechenexperte.de
│
├── tests/             # Automated tests
└── deploy/            # Server configuration and deployment scripts
```

---

## Technology (for interested parties)

| Area | Technology | Why |
| ---- | ---------- | --- |
| Backend | Python + FastAPI | Fast, asynchronous, ideal for AI applications |
| Database | PostgreSQL + pgvector | Relational data + AI search in one system |
| AI Model | Anthropic Claude | Best model for conversations and autonomous action |
| Embeddings | OpenAI | Cheap, proven vectorization for knowledge search |
| Chat | WebSocket | Real-time communication without page reload |
| Widget | React + Vite | Small bundle, runs isolated on any website |
| Dashboard | React + Tailwind | Modern, maintainable admin interface |
| Hosting Backend | Hetzner (EU) | GDPR-compliant, reliable, cost-effective |
| Hosting Frontend | Cloudflare Pages | Global CDN, automatic SSL certificates, free |

---

## Local Setup (for developers)

```bash
# 1. Clone repository
git clone https://github.com/KonstantinData/KI-Mitarbeiter-Team-Kuechen-und-Moebelgeschaeft.git
cd KI-Mitarbeiter-Team-Kuechen-und-Moebelgeschaeft

# 2. One-time setup (Python venv + all dependencies)
./setup.sh

# 3. Configure environment variables
cp .env.example .env
# Open .env and enter API keys

# 4. Set up database
source venv/bin/activate
make migrate

# 5. Start backend
make dev
# → http://localhost:8000/health
# → http://localhost:8000/docs (API documentation)

# 6. Build widget (optional)
cd frontends/widget && pnpm install && pnpm build

# 7. Build dashboard (optional)
cd frontends/dashboard && pnpm install && pnpm build
```

**Required:** Python 3.12+, Node.js 20+, pnpm, PostgreSQL 16 with pgvector

---

## Project Status

| Area | Status |
| ---- | ------ |
| Database schema | Complete |
| API framework | Complete (endpoints as placeholders) |
| WebSocket chat | Complete (echo mode, no agent behind it yet) |
| Agent core (base) | Complete |
| Agent template | Complete |
| Chat widget | Complete, live at `widget.mein-kuechenexperte.de` |
| Admin dashboard | Complete, live at `app.mein-kuechenexperte.de` |
| Agent Lisa | In planning |
| Agent Max | In planning |
| Agents Anna, Tom, Sara | In planning |
| Google Calendar integration | Prepared, not yet activated |
| Email sending | Prepared, not yet activated |

---

## Contact

This project is being developed by **Konstantin** as part of building [mein-kuechenexperte.de](https://www.mein-kuechenexperte.de).

Questions, feedback, or interested in collaboration? → GitHub Issues or directly via email.
