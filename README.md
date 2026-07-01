# JobBoard API

[![CI](https://github.com/Apurvastha/jobboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Apurvastha/jobboard/actions/workflows/ci.yml)

A production-ready job board REST API built with Django and Django REST Framework, targeting backend engineering roles at Japanese product companies.

## Live Demo

- **Swagger UI:** https://jobboard-production-aae7.up.railway.app/api/schema/swagger-ui/
- **ReDoc:** https://jobboard-production-aae7.up.railway.app/api/schema/redoc/
- **API Base:** https://jobboard-production-aae7.up.railway.app/api/v1/
- **Admin Panel:** https://jobboard-production-aae7.up.railway.app/admin/

## Test Credentials

**Candidate account:**
- Username: `alice`
- Password: `testpass123`

**Company account:**
- Username: `mercari`
- Password: `testpass123`

**Quick start:**
1. Open [Swagger UI](https://jobboard-production-aae7.up.railway.app/api/schema/swagger-ui/)
2. `POST /api/v1/accounts/token/` with the credentials above
3. Click **Authorize** (top right lock icon) and paste the access token
4. Explore all endpoints with live data

---

## Tech Stack

- **Backend:** Python 3.11, Django 5.2, Django REST Framework
- **Database:** PostgreSQL 15
- **Cache & Queue:** Redis 7, Celery 5
- **Auth:** JWT (djangorestframework-simplejwt) with token blacklisting
- **Docs:** Swagger / OpenAPI (drf-spectacular)
- **Monitoring:** Sentry (errors + performance)
- **Containerisation:** Docker, Docker Compose
- **CI/CD:** GitHub Actions → Railway (auto-deploy on green CI)
- **Deployment:** Railway

---

## Features

- [x] Multi-app architecture (accounts, jobs, applications, blog, notifications)
- [x] Custom User model with roles (company / candidate / admin)
- [x] Full model layer — job listings, applications, blog, company and candidate profiles
- [x] Database indexes for query optimisation (composite and single-column)
- [x] Django Admin with bulk actions, inlines, and custom dashboards
- [x] N+1 free queries via select_related and prefetch_related (EXPLAIN ANALYZE verified)
- [x] Function-based and class-based views
- [x] Django forms with multi-level validation
- [x] Custom middleware — request logging, audit trail, maintenance mode, JSON error handling
- [x] Django signals — auto profile creation, application notifications, cache invalidation
- [x] JWT authentication with custom claims (role, email, username embedded in token)
- [x] JWT token blacklisting — logout invalidates tokens server-side immediately
- [x] Redis-based access token revocation — logout immediately invalidates access tokens via JTI blacklist with auto-expiring TTL
- [x] Token rotation — stolen refresh tokens detected and invalidated automatically
- [x] Role-based permissions — IsCompany, IsCandidate, IsOwnerOrReadOnly
- [x] DRF serializers with read/write split and nested representations
- [x] ViewSets and Routers with custom @action endpoints (featured, similar, applications)
- [x] django-filter with FilterSet, SearchFilter, OrderingFilter
- [x] Custom pagination with total pages and page metadata
- [x] Redis caching with signal-based invalidation and mutex locks to prevent cache stampede — load-tested and tuned (see Load Testing section)
- [x] Rate limiting — 5/min on login, 100/day unauthenticated, 1000/day authenticated
- [x] Security headers — HSTS, XSS protection, clickjacking prevention, secure cookies
- [x] Health check endpoint — lightweight liveness probe at /health/
- [x] Sentry error monitoring — Django, Celery, and Redis integrations
- [x] Swagger / OpenAPI docs via drf-spectacular
- [x] Seed management command for reproducible test data
- [x] Dockerized with Docker Compose (web + PostgreSQL + Redis + Celery + Beat + Flower)
- [x] Async email notifications via Celery (application received, status change, welcome)
- [x] Celery worker with retry logic (max 3 retries, 60s backoff) and Flower monitoring
- [x] Celery Beat scheduled tasks (nightly job expiry, weekly digest, daily reminders)
- [x] Application system with full status lifecycle (pending → reviewing → accepted/rejected)
- [x] Nested endpoint: GET /jobs/{id}/applications/ for company dashboard
- [x] 68 pytest tests passing — 84% coverage
- [x] GitHub Actions CI pipeline — tests + linting on every push
- [x] Deployed to Railway with automatic CD pipeline

---

## Notification Service Integration

JobBoard is paired with a dedicated [notification-service](https://github.com/Apurvastha/notification-service) — a FastAPI microservice that handles real-time delivery, notification storage, and WebSocket push.

**Live:** https://notification-service-production-ae8f.up.railway.app/docs

### How they connect

Both services share the same JWT secret. A token issued by JobBoard is valid in the notification-service — candidates log in once and the same token works for WebSocket connections. No separate registration required.

### Real-time flow
Company changes application status in JobBoard

→ Django signal detects old vs new status

→ Celery fires HTTP POST to notification-service /notifications/

→ Notification stored in PostgreSQL

→ WebSocket push to candidate's active connection

→ Candidate sees update instantly without refreshing

### Connect as a candidate

```bash
# 1. get a token from JobBoard
POST /api/v1/accounts/token/  →  copy the access token

# 2. start notification-service locally
uvicorn app.main:app --reload --port 8001

# 3. connect WebSocket with your JobBoard token
wscat -c "ws://localhost:8001/ws/notifications?token=<access_token>"

# 4. trigger a status change via JobBoard Swagger
# → notification arrives in wscat terminal in real time
```

## Database Schema

**JobBoard Schema**
![JobBoard Schema](docs/jobboard_schema.png)

**Blog Schema**
![Blog Schema](docs/blog_schema.png)

---

## Project Structure

```
jobboard/
├── accounts/        # custom user model, JWT auth, logout, company and candidate profiles
├── jobs/            # job listings, categories, tags, filtering, caching, Beat tasks
├── applications/    # candidate applications and status lifecycle
├── blog/            # blog posts, comments, self-referential comment threads
├── notifications/   # notification system
├── tests/           # pytest test suite
│   ├── conftest.py
│   ├── test_jobs.py
│   ├── test_accounts.py
│   ├── test_applications.py
│   └── test_cache.py
└── docs/
    ├── jobboard_schema.png
    └── blog_schema.png
```

---

## Local Setup (with Docker)

```bash
git clone https://github.com/Apurvastha/jobboard.git
cd jobboard
cp .env.example .env   # fill in your values
docker-compose up --build -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_data
docker-compose exec web python manage.py createsuperuser
```

Visit:
- API: http://localhost:8000/api/v1/jobs/
- Swagger: http://localhost:8000/api/schema/swagger-ui/
- Admin: http://localhost:8000/admin/
- Flower: http://localhost:5555/

## Local Setup (without Docker)

```bash
git clone https://github.com/Apurvastha/jobboard.git
cd jobboard
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # fill in your values
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py runserver
```

---

## Environment Variables

```
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=jobboard_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=587
EMAIL_HOST_USER=your_mailtrap_username
EMAIL_HOST_PASSWORD=your_mailtrap_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@jobboard.com
SENTRY_DSN=your_sentry_dsn  # optional — error monitoring
NOTIFICATION_SERVICE_URL=your-notification-url
```

---

## API Documentation

Interactive API documentation:

- **Swagger UI:** https://jobboard-production-aae7.up.railway.app/api/schema/swagger-ui/
- **ReDoc:** https://jobboard-production-aae7.up.railway.app/api/schema/redoc/
- **OpenAPI Schema:** https://jobboard-production-aae7.up.railway.app/api/schema/

Local:
- **Swagger UI:** http://localhost:8000/api/schema/swagger-ui/

---

## Key API Endpoints

```
Authentication
  POST   /api/v1/accounts/token/              # login — returns JWT access + refresh tokens
  POST   /api/v1/accounts/token/refresh/      # refresh access token (rotates refresh token)
  POST   /api/v1/accounts/logout/             # logout — blacklists refresh token immediately
  POST   /api/v1/accounts/register/candidate/ # register as candidate
  POST   /api/v1/accounts/register/company/   # register as company
  GET    /api/v1/accounts/me/                 # current user info

Jobs
  GET    /api/v1/jobs/                        # list jobs (filterable, searchable, paginated)
  POST   /api/v1/jobs/                        # create job (company only)
  GET    /api/v1/jobs/{id}/                   # job detail
  PATCH  /api/v1/jobs/{id}/                   # update job (owner only)
  DELETE /api/v1/jobs/{id}/                   # soft delete (owner only)
  GET    /api/v1/jobs/featured/               # top 5 highest paying jobs
  GET    /api/v1/jobs/{id}/similar/           # jobs in same category
  GET    /api/v1/jobs/{id}/applications/      # all applications for this job (company only)
  GET    /api/v1/jobs/categories/             # all categories (Redis cached, 1hr TTL)

Applications
  POST   /api/v1/applications/               # apply to a job (candidate only)
  GET    /api/v1/applications/               # my applications (candidate) or job apps (company)
  GET    /api/v1/applications/{id}/          # application detail
  PATCH  /api/v1/applications/{id}/status/   # change status (company only)

System
  GET    /health/                             # health check — liveness probe
```

---

## Filtering & Search

```bash
# filter by multiple criteria
GET /api/v1/jobs/?location=Tokyo&job_type=full_time&is_remote=false

# salary range
GET /api/v1/jobs/?min_salary=6000000&max_salary=10000000

# full-text search across title, description, company name
GET /api/v1/jobs/?search=python

# ordering
GET /api/v1/jobs/?ordering=-salary_max   # highest paying first
GET /api/v1/jobs/?ordering=-posted_at    # newest first

# pagination
GET /api/v1/jobs/?page=2&page_size=10
```

---

## Security

- **JWT with blacklisting** — logout invalidates tokens server-side, not just client-side
- **Redis access token revocation** — on logout, the access token's JTI is stored in Redis with a TTL matching the token's remaining lifetime. Every request checks this revocation store (~0.1ms in-memory lookup). Token is blocked instantly. Redis self-cleans when TTL expires — zero maintenance
- **Token rotation** — each refresh issues a new refresh token; reuse of old tokens detected as theft and all sessions invalidated
- **Rate limiting** — login endpoint limited to 5 requests/minute to prevent brute force
- **HSTS** — enforces HTTPS for 1 year including subdomains, submitted to browser preload list
- **Security headers** — XSS protection, content type sniffing prevention, clickjacking prevention
- **Secure cookies** — session and CSRF cookies marked Secure and HttpOnly
- **Sentry monitoring** — all unhandled exceptions captured with full stack traces and request context

---

## Load Testing & Performance Investigation

To validate index design, caching behavior, and concurrency handling under
realistic load — not just assume they work — the app was seeded with
25,000+ synthetic job postings and load-tested locally with
[Locust](https://locust.io/), correlated against `EXPLAIN ANALYZE` output
and container-level resource monitoring (`docker stats`).

### 1. Index verification at scale

At 25,213 rows, `EXPLAIN ANALYZE` was run against every declared index to
confirm the query planner actually uses them — not just that they exist.

| Query | Plan | Selectivity | Time |
|---|---|---|---|
| `is_active + posted_at`, ordered, `LIMIT 20` | Index Scan Backward | ~85% match, but capped by `LIMIT` | **0.45ms** |
| `location = 'Tokyo'` | Bitmap Heap Scan | ~11% | 2.3ms |
| `job_type = 'full_time'` | Bitmap Heap Scan | ~25% | 3.5ms |
| `salary_min >= 6000000` | **Seq Scan** (index skipped — correctly) | ~55% | 6.8ms |
| `description LIKE '%word%'` | Seq Scan (no index can serve this) | ~0% | 7.7ms |

Two results worth calling out specifically: at ~55% selectivity, Postgres
correctly ignores the `salary_min` index in favor of a sequential scan —
verified via planner cost output, not assumed. And no B-tree index can
serve a leading-wildcard `LIKE` query at all, which is a direct preview of
why the planned AI-service will need proper full-text search (GIN +
`pg_trgm` or `tsvector`) rather than relying on Postgres defaults.

### 2. Concurrency load testing — three stages

Tested at 10, 50, and 100 concurrent users against the local Django dev
server (`manage.py runserver`), flushing Redis before each run for a cold
cache:

| Concurrent users | Median | p95 | p99 | RPS | Failures |
|---|---|---|---|---|---|
| 10 | 31ms | 160ms | 320ms | 27.8 | 0 |
| 50 | 290ms | 710ms | 1000ms | 56.6 | 0 |
| 100 | 690ms | 2500ms | 3600ms | 80.7 | **2 / 14,756** |

`docker stats` during the 100-user run showed `jobboard_web` pegged at
80–150% CPU while Postgres stayed under 2% — confirming the degradation
was the single-process dev server's thread-per-request model, not the
database or cache layer.

**The 2 failures were a real, distinct finding:** `FATAL: sorry, too many
clients already` — Postgres's `max_connections` (default 100) was briefly
exhausted, because local dev has no `CONN_MAX_AGE` configured, so every
request opens a fresh DB connection. Production already mitigates this —
`settings.py` sets `conn_max_age=600` for the Railway/`DATABASE_URL`
branch — but this surfaced a real local/production parity gap worth
tracking.

### 3. Cache-stampede lock — isolated testing found and fixed a real bug

General concurrent load isn't a valid test of the cache-stampede mutex
lock specifically — with ~99 distinct job IDs in the request pool, the
odds of many requests colliding on the *same* cold key by chance are low.
A dedicated test was built: every simulated user hits one fixed job ID,
fired as a single simultaneous burst (not a sustained loop) immediately
after a cache flush, compared against an unprotected endpoint
(`/jobs/categories/`, plain cache, no lock) as a control.

The first attempt was confounded by the dev server's queuing overhead
(3000ms+ tail latencies swamping any signal). Re-run against gunicorn
(`--workers 2`, matching the production command) isolated the real effect:

| | Protected (`/jobs/{id}/`) | Unprotected (`/jobs/categories/`) |
|---|---|---|
| Median (before fix) | **410ms** | 240ms |

The lock was making things *slower*, not faster. Root cause: the
lock-losing branch used a single fixed `time.sleep(0.1)` regardless of how
quickly the lock-holder actually finished — every waiter paid the full
100ms even when data was ready in 10–20ms. This also surfaced a previously
identified bug in the same code path: the fallback used
`self.get_serializer(instance)` instead of `.data`, returning a serializer
instance into `Response()` instead of serialized data.

**Fix:** replaced the fixed sleep with a short retry loop (3 attempts,
10ms apart, exiting early once data appears), and fixed the missing
`.data` bug in both `retrieve()` and `featured()` — the same query used to
be duplicated between the lock-winner and fallback paths in `featured()`,
so it was also extracted into a single local helper function to keep both
paths in sync.

| | Before | After | Change |
|---|---|---|---|
| Median | 410ms | **310ms** | **−100ms**, matching the fix's mechanism almost exactly |
| Max | 608ms | 471ms | −137ms |

### What this demonstrates

- Index behavior was verified with real `EXPLAIN ANALYZE` output at
  production-representative scale, not assumed from documentation.
- A general load test surfaced a real Postgres connection-exhaustion bug
  and a local/production configuration gap.
- A *targeted* test — not just "more load" — was needed to properly
  isolate and validate the cache-stampede mutex lock, which in turn
  uncovered and fixed a real correctness bug (`.data`) and a real
  performance regression (fixed-sleep wait strategy) that general testing
  had missed entirely.

---


```bash
docker-compose exec web pytest tests/ -v --cov=. --cov-report=term-missing
```

**68 tests passing · 84% coverage**

| Area | Tests |
|---|---|
| Job listings — CRUD, permissions, filtering, N+1 | 22 tests |
| Authentication — JWT, registration, logout, profiles | 22 tests |
| Applications — apply, status change, permissions | 13 tests |
| Redis cache — invalidation, hit/miss, stampede-lock contention | 6 tests |
| Celery tasks — email, job expiry | 5 tests |

---

## CI/CD Pipeline

Every push to `main`:

```
Push to GitHub
    ↓
GitHub Actions — spin up PostgreSQL + Redis
    ↓
Run migrations + check for missing migrations
    ↓
Run 68 pytest tests (fail if coverage < 70%)
    ↓
Run Ruff linter
    ↓
Deploy to Railway (only if all tests pass)
    ↓
gunicorn starts on Railway
    ↓
Live at https://jobboard-production-aae7.up.railway.app
```

---

## Project Status

Actively in development.