<div align="center">

# Smart Triage System

**An intelligent AI-powered customer support ticket management platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.134-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=nextdotjs)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-NeonDB-336791?style=for-the-badge&logo=postgresql)](https://neon.tech/)
[![Redis](https://img.shields.io/badge/Redis-Cloud-DC382D?style=for-the-badge&logo=redis)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)

> Customers submit tickets. AI classifies them instantly. Agents resolve them fast.

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Live Hosts](#-live-hosts)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Folder Structure](#-folder-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development](#local-development)
  - [Docker (Recommended)](#docker-recommended)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Authentication Flow](#-authentication-flow)
- [Design Decisions & Best Practices](#-design-decisions--best-practices)
- [Security](#-security)
- [RBAC — Role-Based Access Control](#-rbac--role-based-access-control)
- [LLM Resilience](#-llm-resilience)
- [AI Journey](#-ai-journey)

---

## Overview

The **Smart Triage System** is a full-stack web application that streamlines the customer support lifecycle:

1. **Customers** submit support tickets through a clean public form — no login required.
2. **AI (Google Gemini)** automatically classifies each ticket by `category` (billing, technical bug, feature request, other) and `priority` (high, medium, low).
3. **Support Agents** log into a protected dashboard to view, filter, paginate, and update ticket statuses in real-time with optimistic UI updates.

The system is designed with a **separation of concerns** between the public-facing customer portal and the internal agent dashboard, with cookie-based JWT authentication and Redis-backed OTP email verification.

---

## Live Hosts

| Service | URL |
|---|---|
| **Frontend (Customer & Agent Portal)** | `http://localhost:3000` |
| **Backend API** | `http://localhost:8000` |
| **Interactive API Docs (Swagger)** | `http://localhost:8000/docs` |
| **Alternative API Docs (ReDoc)** | `http://localhost:8000/redoc` |

---

## Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.11 | Primary language |
| **FastAPI** | 0.134 | REST API framework — async, high performance |
| **SQLAlchemy** | 2.0 | ORM for database modeling and queries |
| **PostgreSQL (NeonDB)** | Cloud | Primary relational database |
| **Redis (Redis Cloud)** | 7.x | OTP storage with TTL, session caching |
| **python-jose** | 3.x | JWT access & refresh token creation/validation |
| **passlib + bcrypt** | 1.7 | Secure password hashing |
| **pydantic-settings** | 2.x | Type-safe environment variable management |
| **uvicorn** | 0.41 | ASGI server |
| **Google Gemini** | API | AI-powered ticket classification |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| **Next.js** | 14 (App Router) | React framework with SSR support |
| **React** | 18 | UI library |
| **TypeScript** | 5 | Static typing for reliability |
| **Tailwind CSS** | 3.x | Utility-first styling |
| **Shadcn UI** | Latest | Headless, accessible component library |
| **react-hook-form + Zod** | Latest | Form handling with schema validation |
| **sonner** | 1.4 | Toast notification system |
| **lucide-react** | Latest | Icon library |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker + Docker Compose** | Containerised deployment of both services |
| **NeonDB (Serverless Postgres)** | Cloud-hosted database, no infrastructure management |
| **Redis Cloud** | Managed Redis for OTP and session data |

---

## 🏗️ Architecture

```
                          ┌─────────────────────────────┐
                          │         Browser              │
                          │  Customer │ Agent Dashboard  │
                          └────────────┬────────────────┘
                                       │  HTTP
                          ┌────────────▼────────────────┐
                          │     Next.js Frontend         │
                          │        (Port 3000)           │
                          │  - Customer submission page  │
                          │  - Agent login / register    │
                          │  - Protected dashboard       │
                          └────────────┬────────────────┘
                                       │  /api/* proxy (rewrites)
                          ┌────────────▼────────────────┐
                          │     FastAPI Backend           │
                          │        (Port 8000)           │
                          │  - Auth routes (JWT + OTP)   │
                          │  - Ticket CRUD               │
                          │  - AI classification         │
                          └──────┬───────────┬──────────┘
                                 │           │
               ┌─────────────────▼──┐  ┌────▼──────────┐
               │  PostgreSQL (Neon)  │  │  Redis Cloud   │
               │  (Tickets, Agents) │  │  (OTP, Cache)  │
               └────────────────────┘  └───────────────┘
                                               │
                                    ┌──────────▼──────────┐
                                    │   Google Gemini API  │
                                    │  (Ticket Classifier) │
                                    └─────────────────────┘
```

> **Key Design Choice — API Proxy:**
> The Next.js frontend proxies all `/api/*` requests to the FastAPI backend via `next.config.mjs` rewrites.
> This means the browser only ever talks to port 3000, avoiding CORS issues and allowing session cookies to be transmitted correctly on the same origin.

---

## 📁 Folder Structure

```
triage_app/
│
├── 📄 docker-compose.yml          # Spins up both backend + frontend with one command
├── 📄 AI_JOURNEY.md               # AI usage documentation, hallucinations caught, lessons learned
├── 📄 README.md                   # This file
│
├── 🐍 backend/                    # FastAPI Python backend
│   ├── Dockerfile                 # Container build instructions for the backend
│   ├── main.py                    # FastAPI app entrypoint — registers routers, CORS, startup events
│   ├── requirements.txt           # All Python dependencies (pinned versions)
│   ├── .env                       # Environment variables (never committed to git)
│   ├── .gitignore
│   │
│   └── app/
│       ├── api/
│       │   └── v1/                # Versioned API routes
│       │       ├── auth.py        # Register, login, logout, refresh, OTP endpoints
│       │       ├── ticket.py      # Agent-facing ticket list + status update
│       │       ├── customer.py    # Public ticket submission endpoint
│       │       └── router.py      # Aggregates all v1 routes
│       │
│       ├── core/
│       │   └── config.py          # Reads .env via pydantic-settings — single source of truth
│       │
│       ├── db/
│       │   ├── database.py        # SQLAlchemy engine + session factory
│       │   ├── models.py          # ORM models: Tickets, SupportAgent, Enums
│       │   └── dependencies.py    # FastAPI Depends() for DB sessions
│       │
│       ├── schemas/               # Pydantic request/response schemas
│       │   ├── ticket.py          # TicketCreate, TicketResponse, TicketUpdate
│       │   └── auth.py            # RegisterUserRequest, LoginRequest, TokenResponse
│       │
│       ├── services/
│       │   └── v1/
│       │       ├── auth.py        # Business logic: JWT creation, bcrypt, OTP, cookie management
│       │       ├── tickets.py     # Ticket fetch with filters, status update logic
│       │       └── customer.py    # AI classification + ticket creation
│       │
│       ├── agent/                 # AI agent — Gemini integration for classification
│       └── utils/                 # Shared helpers (email, token utilities, etc.)
│
└── ⚛️  frontend/                   # Next.js 14 App Router frontend
    ├── Dockerfile                 # Multi-stage container build (deps → build → runner)
    ├── next.config.mjs            # API proxy rewrite rules + standalone output config
    ├── tailwind.config.js         # Tailwind CSS config with custom animations and colors
    ├── postcss.config.js          # PostCSS config (CommonJS — required by Next.js webpack)
    ├── tsconfig.json              # TypeScript compiler settings
    ├── package.json               # Node.js dependencies
    ├── components.json            # Shadcn UI configuration
    ├── .gitignore                 # Ignores node_modules, .next, .env files
    │
    └── src/
        ├── app/                   # Next.js App Router pages
        │   ├── layout.tsx         # Root layout — wraps all pages with AuthProvider + Toaster
        │   ├── globals.css        # Global styles, CSS variables, dark mode theme, glassmorphism
        │   │
        │   ├── page.tsx           # / → Public Customer Ticket Submission page
        │   │
        │   ├── login/
        │   │   └── page.tsx       # /login → Agent login form
        │   │
        │   ├── register/
        │   │   └── page.tsx       # /register → Agent registration form
        │   │
        │   └── dashboard/
        │       ├── layout.tsx     # Dashboard shell — sticky header with logout + live status dot
        │       └── page.tsx       # /dashboard → Ticket table with filters, pagination, status updates
        │
        ├── components/
        │   ├── providers/
        │   │   └── auth-provider.tsx  # React Context for auth state + route protection
        │   │
        │   └── ui/                # Shadcn UI component library
        │       ├── button.tsx
        │       ├── card.tsx
        │       ├── input.tsx
        │       ├── select.tsx
        │       ├── table.tsx
        │       ├── badge.tsx
        │       ├── label.tsx
        │       ├── textarea.tsx
        │       └── sonner.tsx     # Toast wrapper
        │
        └── lib/
            ├── api.ts             # Typed API client for all backend endpoints
            └── utils.ts           # Tailwind class merge utility (cn)
```

---

## Getting Started

### Prerequisites

Make sure the following are installed on your machine:

- **Node.js** ≥ 18 — [Download](https://nodejs.org/)
- **Python** ≥ 3.11 — [Download](https://www.python.org/)
- **Docker Desktop** (optional, for Docker setup) — [Download](https://www.docker.com/)

---

### Local Development

Run the backend and frontend in separate terminals.

#### Backend

```bash
# 1. Navigate to the backend folder
cd triage_app/backend

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Ensure .env is populated (see Environment Variables section)

# 5. Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# → API available at http://localhost:8000
# → Swagger docs at http://localhost:8000/docs
```

#### Frontend

```bash
# 1. Navigate to the frontend folder
cd triage_app/frontend

# 2. Install Node.js dependencies
npm install

# 3. Start the Next.js development server
npm run dev
# → App available at http://localhost:3000
```

---

### Docker (Recommended)

Use Docker Compose to spin up **both services with a single command** from the project root:

```bash
# Navigate to the project root
cd triage_app

# Build images and start both services
docker-compose up --build

# To run in the background (detached mode)
docker-compose up --build -d

# To stop all running containers
docker-compose down
```

After startup:
- **Frontend** → `http://localhost:3000`
- **Backend API** → `http://localhost:8000`
- **Swagger Docs** → `http://localhost:8000/docs`

> **Note:** The first `--build` takes a few minutes as it compiles Next.js and installs Python packages. Subsequent `docker-compose up` runs are significantly faster.

---

## Environment Variables

Create a `.env` file inside the `backend/` directory with the following variables:

```dotenv
# ── Application ─────────────────────────────────────────
PROJECT_NAME="Smart Triage System"
VERSION=1.0.0
ENVIRONMENT=development       # development | production
DEBUG=True
API_V1_STR=/api/v1
HOST=0.0.0.0
PORT=8000

# ── Security ─────────────────────────────────────────────
SECRET_KEY=your_super_secret_key_here   # Generate with: openssl rand -hex 64
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15          # Short-lived access tokens
REFRESH_TOKEN_EXPIRE_DAYS=60            # Long-lived refresh tokens

# ── Database ─────────────────────────────────────────────
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# ── Redis ─────────────────────────────────────────────────
REDIS_HOST=your_redis_host
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# ── OTP ────────────────────────────────────────────────────
OTP_EXPIRE_MINUTES=10                   # OTP expires after 10 minutes

# ── Google AI ─────────────────────────────────────────────
GOOGLE_API_KEY=your_google_gemini_api_key

# ── CORS ──────────────────────────────────────────────────
CORS_ORIGINS='["http://localhost:3000", "http://127.0.0.1:3000"]'
```

> **Never commit `.env` files to version control.** The `.gitignore` in both `backend/` and `frontend/` already excludes them.

---

## 📡 API Reference

All routes are prefixed with `/api/v1`. The frontend proxies these automatically.

### Authentication — `/api/v1/auth`

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/register` | ❌ | Register a new support agent |
| `POST` | `/login` | ❌ | Login — sets access + refresh cookies |
| `POST` | `/logout` | ✅ | Clear session cookies |
| `POST` | `/refresh` | ✅ (cookie) | Issue a new access token using the refresh token |
| `POST` | `/send-verification-otp` | ✅ | Send OTP email to agent |
| `POST` | `/verify-otp` | ✅ | Verify OTP code, mark agent as verified |

### Tickets — `/api/v1/ticket`

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/ticket` | ✅ | List tickets with pagination & filters |
| `PATCH` | `/ticket/{ticket_id}` | ✅ | Update ticket status |

**Query parameters for `GET /ticket`:**

| Param | Type | Description |
|---|---|---|
| `skip` | integer | Number of records to skip (pagination offset) |
| `limit` | integer | Max records to return (default: 10) |
| `status` | string | Filter by `open`, `in_progress`, `resolved` |
| `priority` | string | Filter by `high`, `medium`, `low` |
| `category` | string | Filter by `billing`, `technical_bug`, `feature_request`, `other` |

### Customer — `/api/v1/customer`

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/ticket` | ❌ | Submit a new support ticket (public) |

---

## 🔑 Authentication Flow

```
Agent Registration:
  POST /register → hash password (bcrypt) → store in DB → return agent ID

Agent Login:
  POST /login
    → verify password
    → create JWT access token (15 min) + refresh token (60 days)
    → set both as httpOnly, SameSite=lax cookies
    → return agent info

OTP Verification:
  POST /send-verification-otp → generate 6-digit OTP → store in Redis (TTL 10 min) → send email
  POST /verify-otp → compare OTP with Redis value → mark agent as verified → delete OTP

Token Refresh:
  POST /refresh → read refresh token from cookie → validate → issue new access token cookie

Logout:
  POST /logout → clear both cookie values → return 200
```

> **Why httpOnly cookies instead of localStorage?**
> `localStorage` is accessible via JavaScript, making it vulnerable to XSS attacks. `httpOnly` cookies cannot be read by JavaScript, only sent automatically by the browser on each request to the same origin — a significantly more secure approach.

---

## Design Decisions & Best Practices

### Backend

| Decision | Rationale |
|---|---|
| **FastAPI over Flask/Django** | Async-first, automatic OpenAPI docs, Pydantic validation built-in, significantly faster |
| **SQLAlchemy 2.0 ORM** | ORM abstracts raw SQL (reduces injection risk), migration-friendly, and integrates cleanly with Pydantic |
| **Versioned API routes (`/api/v1/`)** | Allows future API changes without breaking existing clients |
| **Pydantic schemas separate from ORM models** | Prevents internal DB columns from leaking into API responses (e.g. hashed_password) |
| **Redis for OTP TTL** | A time-based expiry is trivially implemented with Redis `EXPIRE` — no cron jobs or cleanup needed |
| **Sqids for IDs** | Generates short, URL-safe, human-friendly IDs (not UUIDs) without exposing auto-increment integers |
| **Startup event for DB + Redis** | Initialises connections once on startup rather than per-request, improving performance |

### Frontend

| Decision | Rationale |
|---|---|
| **Next.js App Router** | Server components, layouts, and nested routing are cleaner than the Pages Router for this structure |
| **API Proxy via `next.config.mjs`** | Avoids CORS issues and allows cookies to be sent on the same origin without browser restrictions |
| **Optimistic UI updates** | Status changes feel instant — local state updates immediately while the API call happens in the background, with rollback on failure |
| **Zod + react-hook-form** | Type-safe schema validation colocated with the form component; errors surface at the right level |
| **Shadcn UI** | Headless components that are fully customisable — not a black box like Bootstrap or MUI |
| **`output: standalone`** | Produces a minimal Docker image — only the Node.js server and required files, not the entire `node_modules` |
| **CommonJS PostCSS/Tailwind configs** | Next.js's webpack PostCSS loader uses `require()` — `.mjs` or `.ts` config files cannot be loaded and silently produce zero CSS output |

### Containerisation

| Decision | Rationale |
|---|---|
| **Separate Dockerfile per service** | Follows Docker best practice of one process per container — independently scalable and restartable |
| **Multi-stage frontend Dockerfile** | The final image only contains the compiled output and Node.js server, not build tools or `node_modules` (reduces image size dramatically) |
| **`docker-compose.yml` at root** | One command (`docker-compose up --build`) builds and starts the entire stack |
| **`BACKEND_URL` env variable** | Inside Docker, containers communicate by service name, not `localhost`. The env var switches the API proxy target between local dev and Docker without code changes |

---

## 🔒 Security

- **Passwords** are hashed with `bcrypt` (via `passlib`) — never stored in plaintext
- **JWTs** are stored in `httpOnly`, `SameSite=lax` cookies — immune to JavaScript-based XSS theft
- **OTPs** have a 10-minute TTL enforced by Redis — expired automatically, no db cleanup needed
- **Email verification** gates full agent access — unverified agents cannot interact with tickets
- **CORS** is configured to allow only trusted origins in production
- **Pydantic schemas** enforce strict input validation on every API endpoint — malformed requests are rejected before hitting business logic
- **Environment variables** manage all secrets — never hardcoded in source code

---

## RBAC — Role-Based Access Control

> *This section answers the Verification Task requirement*

The current system has one agent role. Here is how RBAC would be extended to support **Admin** and **Read-Only** roles:

### Step 1 — Add a `role` column to the database model

```python
# backend/app/db/models.py

class AgentRole(str, Enum):
    admin     = "admin"      # Full access + manage agents
    agent     = "agent"      # Default — can update tickets
    read_only = "read_only"  # View-only, no mutations

class SupportAgent(Base):
    ...
    role = Column(DbEnum(AgentRole), default=AgentRole.agent, nullable=False)
```

### Step 2 — Encode the role in the JWT

```python
# At login, include role in payload so every request is self-contained
access_token = create_access_token({"sub": agent.id, "role": agent.role})
```

### Step 3 — Create permission dependency functions

```python
# backend/app/api/dependencies.py

def require_admin(current_agent = Depends(get_current_agent)):
    if current_agent.role != AgentRole.admin:
        raise HTTPException(403, "Admin access required")
    return current_agent

def require_write(current_agent = Depends(get_current_agent)):
    if current_agent.role == AgentRole.read_only:
        raise HTTPException(403, "Read-only users cannot modify data")
    return current_agent
```

### Step 4 — Apply to routes

| Action | Allowed Roles |
|---|---|
| View tickets | `admin`, `agent`, `read_only` |
| Update ticket status | `admin`, `agent` |
| Delete tickets | `admin` only |
| Register new agents | `admin` only |

---

## LLM Resilience

> *This section answers the Verification Task requirement*

The Smart Triage System uses **Google Gemini** to auto-classify submitted tickets. If the LLM API is unavailable, the system **degrades gracefully** — ticket submission never fails.

### How failure is handled

```python
# backend/app/services/v1/customer.py

try:
    # Attempt AI classification
    classification = await classify_ticket_with_gemini(title, description)
    ticket.priority = classification.priority
    ticket.category = classification.category
except Exception as e:
    # LLM is down — log and fall back to safe defaults
    logger.warning(f"LLM classification failed: {e}")
    ticket.priority = TicketPriority.low
    ticket.category = TicketCategory.other

# Ticket is always saved regardless of LLM outcome
db.add(ticket)
db.commit()
```

### Impact during an outage

| Scenario | Behaviour |
|---|---|
| LLM responds normally | Ticket is classified and saved with correct category/priority |
| LLM times out or errors | Ticket is saved with `priority=low`, `category=other` |
| Customer experience | Unaffected — they always receive a success response |
| Agent experience | Affected tickets show as `other/low` — agents can correct manually via dashboard |

This follows the **"LLM as enhancement, not dependency"** principle — AI improves the system but the core workflow never blocks on it.

---

## AI Journey

See [AI_JOURNEY.md](./AI_JOURNEY.md) for a full account of:
- The 3 complex prompts used to generate core boilerplate
- Two documented cases of AI hallucination/bad practice that were caught and fixed
- Extended answers to the RBAC and LLM resilience prompts above

---

<div align="center">

Built with using FastAPI, Next.js, and Google Gemini

</div>
