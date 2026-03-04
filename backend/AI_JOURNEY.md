#  AI Journey, Smart Triage System

This document records how AI assistance was used throughout the development of the Smart Triage System — what worked, what went wrong, and the lessons learned.

---

## 1. Complex Prompts Used

### Prompt 1: Database Schema & ORM Model Generation

**Prompt given to AI:**

> "Design a SQLAlchemy ORM schema for a customer support triage system. There should be a `Tickets` table with a category (billing, technical bug, feature request, other), status (open, in_progress, resolved), and priority (high, medium, low). Use Python Enums for these values, and generate human-readable but unique IDs using sqids (timestamp + random). There should also be a `SupportAgent` table with hashed_password, email verification status, and name."

**What was generated:**

The AI produced the complete `models.py` with `TicketCategory`, `TicketStatus`, and `TicketPriority` Python Enums mapped to SQLAlchemy `DbEnum` columns, the `Tickets` and `SupportAgent` models, and the `sqids`-based ID generation lambda using `int(time.time() * 1000)` combined with a random integer for uniqueness.

**Why it was complex:**

It required integrating multiple libraries (SQLAlchemy ORM, sqids, Python Enum) into a coherent schema in a single pass, and correctly mapping string Enums to database-level ENUM types.

---

### Prompt 2: JWT + OTP Authentication Service

**Prompt given to AI:**

> "Write a complete FastAPI authentication service that supports: agent registration with bcrypt password hashing, login that issues an access token (JWT, 15 min expiry) in an httpOnly cookie and a refresh token (JWT, 60 days) also in a cookie, an OTP email verification flow using Redis to store the OTP with a 10-minute TTL, a token refresh endpoint that reads from the cookie, and a logout endpoint that clears the cookies. Use python-jose for JWTs. Make the cookie secure and SameSite=lax."

**What was generated:**

A full `auth.py` service with all the above features — bcrypt hashing via `passlib`, `python-jose` for JWT encoding/decoding, Redis for OTP storage with `EXPIRE`, and cookie management using FastAPI's `Response` object. The OTP flow included both a send endpoint (with a random 6-digit OTP) and a verify endpoint that validates against the Redis-stored value.

**Why it was complex:**

Coordinating stateless JWTs (stored in cookies) with stateful OTP verification (Redis TTL), plus secure cookie configuration (httpOnly, SameSite, Secure flags) in FastAPI is a multi-step flow that typically requires significant boilerplate.

---

### Prompt 3: Next.js Agent Dashboard with Optimistic UI, Pagination & Filtering

**Prompt given to AI:**

> "Build a Next.js App Router dashboard page for support agents. It should fetch tickets from `GET /api/v1/ticket/ticket` with `skip`, `limit`, `status`, `priority`, and `category` query parameters. Display them in a Shadcn UI table. Allow agents to change ticket status via a Select dropdown with an optimistic UI update (update the local state immediately and revert if the API call fails). Add pagination controls (Previous/Next buttons based on whether the response returned fewer items than the limit). Add filter selects for status, priority, and category that reset pagination when changed."

**What was generated:**

The complete `dashboard/page.tsx` with `useCallback`-memoised fetch logic, optimistic `setTickets` mutation before the API call, revert-on-error with a re-fetch, and controlled pagination using a `skip` state variable. The filter selects reset `skip` to 0 on change to avoid showing an empty page 2 after filtering.

**Why it was complex:**

Combining server state (API fetch), optimistic local state mutations, pagination that interacts with filters, and error recovery into a single clean React component without a third-party data-fetching library.

---

## 2. AI Hallucinations & Bad Practices Caught

### Instance: Category Enum Mismatch (Silently Wrong Values)

**What the AI produced:**

When generating the frontend filter dropdowns for ticket categories, the AI used display-friendly labels and mapped them to values like `"technical"`, `"general"`, and `"billing"`. For example:

```tsx
<SelectItem value="technical">Technical</SelectItem>
<SelectItem value="general">General</SelectItem>
```

**What was wrong:**

The backend `TicketCategory` enum in `models.py` uses `"technical_bug"` and `"other"` — not `"technical"` and `"general"`. This meant filtering by category silently returned zero results — no error was thrown, the query just matched nothing.

**How it was caught:**

When clicking the "Technical" filter in the dashboard, the table showed zero tickets even though there were known technical tickets in the database. Comparing the API response (`ticket.category == "technical_bug"`) against the filter value being sent (`?category=technical`) made the mismatch obvious.

**How it was fixed:**

The filter `SelectItem` values were corrected to exactly match the backend enum string values:

```tsx
<SelectItem value="technical_bug">Technical Bug</SelectItem>
<SelectItem value="feature_request">Feature Request</SelectItem>
<SelectItem value="billing">Billing</SelectItem>
<SelectItem value="other">Other</SelectItem>
```

**Lesson learned:**

The AI optimised for human-readable UI labels and subtly decoupled them from the actual API contract without flagging this. Any time AI generates frontend values that must match a backend enum, always cross-reference against the actual schema — the AI will not always do this automatically.

---

### Instance: PostCSS Config in Wrong Module Format

**What the AI produced:**

The AI generated `postcss.config.mjs` (ES Module format) and `tailwind.config.ts` (TypeScript) as the configuration files.

**What was wrong:**

Next.js's internal PostCSS webpack loader uses CommonJS `require()` to load the PostCSS config. An `.mjs` file is not loadable via `require()` in this context, and `tailwind.config.ts` requires a TypeScript transpiler that isn't available during the PostCSS pipeline. The result was that PostCSS ran but silently skipped Tailwind — serving the raw `@tailwind base;` directives to the browser as plain text, which the browser ignored entirely, resulting in zero styling.

**How it was caught:**

Inspecting the compiled output in `.next/static/css/app/layout.css` showed the raw `@tailwind base;` directives still present, instead of compiled CSS. This confirmed PostCSS never executed the Tailwind plugin.

**How it was fixed:**

Both config files were replaced with CommonJS equivalents:
- `postcss.config.mjs` → `postcss.config.js` (using `module.exports`)
- `tailwind.config.ts` → `tailwind.config.js` (using `module.exports`)

The old files were deleted to prevent ambiguous resolution, and the `.next` cache was cleared to force a full recompile.

---

## 3. Verification Task Answers

### A. How Would You Implement RBAC for Admin and Read-Only Users?

The current system has a single agent role. To support Admins and Read-Only users, the following changes would be made:

**1.Add a `role` column to the `SupportAgent` model:**

```python
class AgentRole(str, Enum):
    admin     = "admin"
    agent     = "agent"
    read_only = "read_only"

class SupportAgent(Base):
    ...
    role = Column(DbEnum(AgentRole), default=AgentRole.agent, nullable=False)
```

**2. Encode the role in the JWT payload** at login time so every request carries the role without a DB lookup:

```python
access_token = create_access_token({"sub": agent.id, "role": agent.role})
```

**3. Create FastAPI permission dependencies:**

```python
def require_admin(current_agent = Depends(get_current_agent)):
    if current_agent.role != AgentRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_agent

def require_write(current_agent = Depends(get_current_agent)):
    if current_agent.role == AgentRole.read_only:
        raise HTTPException(status_code=403, detail="Read-only users cannot modify data")
    return current_agent
```

**4. Apply dependencies to routes:**

| Action | Allowed Roles |
|---|---|
| View tickets | admin, agent, read_only |
| Update ticket status | admin, agent |
| Delete tickets | admin only |
| Register new agents | admin only |

Read-Only users can query all data but any `POST` / `PATCH` / `DELETE` route would raise a `403 Forbidden`.

---

### B. What Happens If the LLM API Goes Down?

The Smart Triage System uses an LLM (via Google Gemini API) to **auto-classify** submitted tickets — assigning `category` and `priority` automatically rather than leaving them as defaults.

**Design for graceful degradation:**

The LLM call is wrapped in a `try/except` block. If the API is unavailable, times out, or returns an error, the ticket is still saved to the database with safe default values (`priority=low`, `category=other`):

```python
try:
    classification = await classify_ticket_with_llm(title, description)
    ticket.priority = classification.priority
    ticket.category = classification.category
except Exception:
    # LLM is down — fall back to defaults, ticket is still created
    ticket.priority = TicketPriority.low
    ticket.category = TicketCategory.other
```

**What this means in practice:**

- Customers can always submit tickets — the submission endpoint never fails due to the LLM.
- Agents can still view and update all tickets.
- New tickets created during an outage will appear with default `low` priority and `other` category, which agents can manually correct via the dashboard status selector.
- The failure is logged so ops teams can identify the outage window and re-classify affected tickets afterwards.

This follows the **"LLM as enhancement, not dependency"** principle — the core CRUD functionality of the triage system works independently of any AI service.