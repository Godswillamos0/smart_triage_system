# Smart Triage System; Backend API

A high-performance, async REST API built with **FastAPI** and **Python 3.11** that powers the Smart Triage System. It handles agent authentication (JWT + OTP), AI-powered ticket classification via Google Gemini, and all ticket management operations.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication-apiv1auth)
  - [Tickets (Agent)](#tickets-agent-apiv1ticket)
  - [Customer (Public)](#customer-public-apiv1customer)
- [Data Models](#data-models)
  - [Tickets Table](#tickets-table)
  - [SupportAgent Table](#supportagent-table)
- [Authentication Flow](#authentication-flow)
- [AI Classification](#ai-classification)
- [Database](#database)
- [Design Decisions](#design-decisions)

---

## Quick Start

```bash
# 1. Clone and navigate to the backend
cd triage_app/backend

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your .env file (see Environment Variables section)

# 5. Start the server with hot-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be live at:
- **Base URL:** `http://localhost:8000`
- **Swagger UI (interactive docs):** `http://localhost:8000/docs`
- **ReDoc (reference docs):** `http://localhost:8000/redoc`

---

## Tech Stack

| Library | Version | Role |
|---|---|---|
| **FastAPI** | 0.134 | Web framework — async, OpenAPI auto-docs |
| **SQLAlchemy** | 2.0 | ORM for database models and queries |
| **PostgreSQL (NeonDB)** | Cloud | Primary relational database |
| **Redis (Redis Cloud)** | 7.x | OTP storage with TTL, session caching |
| **python-jose** | 3.x | JWT access and refresh token signing/verification |
| **passlib + bcrypt** | 1.7 | Secure password hashing — never store plaintext |
| **python-dotenv** | 1.x | Loads `.env` values into `os.environ` |
| **sqids** | 0.5 | Generates short, unique, URL-safe IDs |
| **uvicorn** | 0.41 | ASGI server running the application |
| **Google Gemini (via API)** | — | AI model for ticket category + priority classification |

---

## Folder Structure

```
backend/
│
├── main.py                        # App entrypoint
│                                  # - Creates FastAPI instance
│                                  # - Adds CORS middleware
│                                  # - Registers all routers
│                                  # - Connects to Redis on startup
│                                  # - Runs DB migrations (create_all) on startup
│
├── requirements.txt               # All Python dependencies (pinned versions)
├── .env                           # Environment secrets — never committed to git
├── .gitignore                     # Excludes .venv, __pycache__, .env, test.db
├── Dockerfile                     # Container build instructions
│
└── app/
    │
    ├── api/                       # API route layer — thin, delegates to services
    │   └── v1/                    # All routes versioned under /api/v1
    │       ├── router.py          # Aggregates all v1 sub-routers into one
    │       ├── auth.py            # Auth routes (register, login, OTP, refresh, logout)
    │       ├── ticket.py          # Agent ticket routes (list, update status)
    │       └── customer.py        # Public ticket submission route
    │
    ├── core/
    │   └── config.py              # Reads .env variables — single source of truth for settings
    │                              # All services import constants from here, not from os.getenv()
    │
    ├── db/                        # Database layer
    │   ├── database.py            # SQLAlchemy engine + SessionLocal factory + Base class
    │   ├── models.py              # ORM models: Tickets, SupportAgent, Enum definitions
    │   └── dependencies.py        # FastAPI Depends() yielding a DB session per request
    │
    ├── schemas/                   # Pydantic request/response schemas
    │   ├── auth.py                # LoginRequest, RegisterUserRequest, LoginResponse,
    │   │                          # VerifyOTP, SendOTP, ResetPasswordWithOTP
    │   └── tickets.py             # CreateTicketRequest, TicketResponse, TicketStatusRequest
    │
    ├── services/                  # Business logic layer — all real work happens here
    │   └── v1/
    │       ├── auth.py            # create_agent, login, send_verification_otp,
    │       │                      # verify_user_otp, logout, refresh_tokens,
    │       │                      # forgot_password_otp, reset_password_with_otp
    │       ├── tickets.py         # get_tickets (with filters + pagination), modify_ticket
    │       └── customer.py        # create_ticket → calls AI agent → saves to DB
    │
    ├── agent/                     # AI agent integration
    │   └── ...                    # Google Gemini API calls for ticket classification
    │
    └── utils/                     # Shared utilities
        └── ...                    # Email helpers, token utilities
```

> **Why this layered structure?**
> - `api/` contains only routing — no business logic
> - `services/` contains all business logic — no direct HTTP concerns
> - `schemas/` decouples the API surface from the DB models (no internal fields leak out)
> - `db/` is isolated so the ORM can be swapped without touching routes

---

## Environment Variables

Create a `.env` file in the `backend/` root directory:

```dotenv
# ── Application ──────────────────────────────────────────────────────
PROJECT_NAME="Smart Triage System"
ENVIRONMENT=development                # development | production
DEBUG=True
HOST=0.0.0.0
PORT=8000

# ── Security ──────────────────────────────────────────────────────────
SECRET_KEY=your_64_char_hex_secret_here
# Generate with: python -c "import secrets; print(secrets.token_hex(64))"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15         # Short-lived — reduces attack window
REFRESH_TOKEN_EXPIRE_DAYS=60           # Long-lived — stored in httpOnly cookie

# ── OTP ───────────────────────────────────────────────────────────────
OTP_EXPIRE_MINUTES=10                  # OTP auto-deleted from Redis after this

# ── Database ──────────────────────────────────────────────────────────
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require

# ── Redis ─────────────────────────────────────────────────────────────
REDIS_HOST=your_redis_host
REDIS_PORT=19802
REDIS_PASSWORD=your_redis_password

# ── Email (Zoho SMTP) ─────────────────────────────────────────────────
ZOHO_MAIL=your_zoho_email@zohomail.com
ZOHO_PASSWORD=your_zoho_password
ZOHO_SMTP_HOST=smtp.zoho.com
ZOHO_SMTP_PORT=465

# ── Google Gemini AI ──────────────────────────────────────────────────
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CLIENT_ID=your_google_client_id

# ── CORS ──────────────────────────────────────────────────────────────
CORS_ORIGINS='["http://localhost:3000"]'
```

---

## Running the Server

### Development (with hot-reload)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
# From the project root (triage_app/)
docker-compose up --build
```

---

## API Endpoints

All routes are prefixed with `/api/v1`.

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Auth | Request Body | Description |
|---|---|---|---|---|
| `POST` | `/register` | No | `{email, password, name}` | Register a new agent account |
| `POST` | `/login` | No | `{email, password}` | Login — sets httpOnly JWT cookies, returns token + user_id |
| `POST` | `/logout` | Yes | — | Clears access + refresh token cookies |
| `POST` | `/refresh` | Yes (cookie) | — | Issues a new access token using the refresh cookie |
| `POST` | `/send-verification-otp` | Yes | `{email}` | Emails a 6-digit OTP to the agent |
| `POST` | `/verify-otp` | Yes | `{email, otp}` | Validates OTP, marks agent as verified |
| `POST` | `/forgot-password` | No | `{email}` | Sends a password-reset OTP |
| `POST` | `/reset-password` | No | `{email, otp, new_password}` | Resets password after OTP verification |

**Example — Register:**
```json
POST /api/v1/auth/register
{
  "email": "agent@company.com",
  "password": "SecurePass123",
  "name": "John Smith"
}
```

**Example — Login response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user_id": "abc123xyz"
}
// + Sets httpOnly cookies: access_token, refresh_token
```

---

### Tickets — Agent (`/api/v1/ticket`)

> Requires valid `access_token` cookie (set at login).

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/ticket` | List tickets with optional filters and pagination |
| `PATCH` | `/ticket/{ticket_id}` | Update ticket status |

**GET `/ticket` — Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `skip` | `int` | `0` | Pagination offset (number of records to skip) |
| `limit` | `int` | `50` | Max records to return |
| `status` | `string` | — | Filter: `open`, `in_progress`, `resolved` |
| `priority` | `string` | — | Filter: `high`, `medium`, `low` |
| `category` | `string` | — | Filter: `billing`, `technical_bug`, `feature_request`, `other` |

**PATCH `/ticket/{ticket_id}` — Request Body:**
```json
{
  "status": "in_progress"   // "open" | "in_progress" | "resolved"
}
```

**Example — Ticket response:**
```json
{
  "id": "abc123xyz0",
  "title": "Cannot login to my account",
  "description": "Getting a 403 error since this morning...",
  "status": "open",
  "priority": "high",
  "category": "technical_bug"
}
```

---

### Customer — Public (`/api/v1/customer`)

> No authentication required — this is the public-facing endpoint.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ticket` | Submit a new support ticket |

**Request Body:**
```json
{
  "title": "My invoice shows the wrong amount",
  "description": "I was charged $120 but my plan is $80/month..."
}
```

**What happens internally:**
1. Request is validated by Pydantic
2. Ticket is sent to Google Gemini for classification (`category` + `priority`)
3. If Gemini fails → fallback to `category=other`, `priority=low`
4. Ticket is saved to PostgreSQL with a unique sqids-generated ID
5. `201 Created` response is returned to the customer

---

## Data Models

### Tickets Table

```python
class Tickets(Base):
    __tablename__ = "tickets"

    # Short, URL-safe ID generated from timestamp + random int using sqids
    id          = Column(String, primary_key=True, default=lambda: sqids.encode([...]))
    
    category    = Column(DbEnum(TicketCategory), default=TicketCategory.other)
    # Values: "billing" | "technical_bug" | "feature_request" | "other"

    status      = Column(DbEnum(TicketStatus), default=TicketStatus.open)
    # Values: "open" | "in_progress" | "resolved"

    priority    = Column(DbEnum(TicketPriority), nullable=False)
    # Values: "high" | "medium" | "low"

    title       = Column(String, nullable=False)
    description = Column(String, nullable=False)
```

### SupportAgent Table

```python
class SupportAgent(Base):
    __tablename__ = "support_agents"

    id              = Column(String, primary_key=True, default=lambda: sqids.encode([...]))
    name            = Column(String, nullable=False)
    email           = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)  # bcrypt hash — never plaintext
    is_verified     = Column(Boolean, default=False)  # True after OTP verification
```

> **Why sqids over UUID?**
> UUIDs look like `27975a3b-092c-41d1-b39b-812acbbf76c4`. Sqids look like `abc123xyz0`. Both are unique, but sqids are shorter, human-readable, and don't expose auto-increment integers that could enumerate records.

---

## Authentication Flow

```
REGISTER:
  POST /auth/register
    → Validate email uniqueness
    → Hash password with bcrypt (cost factor 12)
    → Save SupportAgent to DB (is_verified=False)
    → Return {id, email, is_verified}

LOGIN:
  POST /auth/login
    → Verify email exists + bcrypt.verify(password, hash)
    → Create JWT access token  (HS256, 15 min expiry)
    → Create JWT refresh token (HS256, 60 day expiry)
    → Set both as httpOnly, SameSite=lax cookies on the response
    → Return {access_token, refresh_token, token_type, user_id}

OTP VERIFICATION:
  POST /auth/send-verification-otp
    → Generate random 6-digit OTP
    → Store in Redis: key="otp:{email}", value=OTP, TTL=600s
    → Send OTP via Zoho SMTP email

  POST /auth/verify-otp
    → Redis GET "otp:{email}" → compare with submitted OTP
    → If match: set agent.is_verified=True, Redis DEL "otp:{email}"
    → If expired/wrong: 400 error

TOKEN REFRESH:
  POST /auth/refresh
    → Read refresh_token from cookie
    → Verify signature + expiry with python-jose
    → Issue new access_token cookie

LOGOUT:
  POST /auth/logout
    → Overwrite both cookies with empty values + past expiry
    → Return 200 OK
```

---

## AI Classification

When a customer submits a ticket, the description is sent to **Google Gemini** to determine:
- **Category:** `billing`, `technical_bug`, `feature_request`, or `other`
- **Priority:** `high`, `medium`, or `low`

```python
# Graceful degradation — ticket is ALWAYS saved even if AI fails
try:
    result = await classify_with_gemini(title, description)
    ticket.category = result.category
    ticket.priority = result.priority
except Exception:
    # Gemini API is down or rate-limited — use safe defaults
    ticket.category = TicketCategory.other
    ticket.priority = TicketPriority.low
```

This design ensures the customer-facing submission endpoint **never fails** due to an AI outage.

---

## Database

The backend uses **NeonDB** (serverless PostgreSQL) in production. Tables are created automatically on startup via:

```python
# main.py — runs on every startup
models.Base.metadata.create_all(bind=engine)
```

The SQLAlchemy engine is configured with:
- `pool_pre_ping=True` — validates connections before use (handles cloud DB sleep/timeout)
- `echo=True` — logs all SQL in development for debugging

For local testing, the fallback is SQLite (`SQL_DATABASE_URL=sqlite:///./test.db`).

---

## Design Decisions

| Decision | Why |
|---|---|
| **Layered architecture (api → service → db)** | Each layer has one responsibility. Routes stay thin. Logic is testable in isolation. |
| **Pydantic schemas separate from ORM models** | `hashed_password` and internal DB fields never appear in API responses |
| **httpOnly cookies for JWTs** | Immune to JavaScript XSS theft. Browser sends them automatically — no client-side token management needed |
| **Redis for OTP TTL** | Redis `EXPIRE` handles automatic cleanup — no cron jobs, no stale OTPs in the DB |
| **Short access token (15 min) + long refresh (60 days)** | Limits the damage window if an access token is ever intercepted |
| **`pool_pre_ping=True` on SQLAlchemy engine** | NeonDB serverless scales to zero — connections can drop. Pre-ping reconnects transparently |
| **Versioned routes (`/api/v1/`)** | Future breaking changes go to `/api/v2/` — old clients keep working |
| **sqids for IDs** | Short, URL-safe IDs that don't expose sequential integers (which could enumerate records) |
| **AI as enhancement, not dependency** | LLM classification is best-effort — the core ticket workflow never blocks on it |
