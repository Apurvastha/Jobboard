# Backend Engineering Roadmap — Japan Job Target
**Target:** Backend Engineer / AI Backend Engineer at Japanese tech companies  
**Interview Window:** October 2026 – January 2027  
**Primary Stack:** Python · Django · DRF · FastAPI · PostgreSQL · Redis · Celery · Docker  
**Portfolio Project:** [JobBoard API](https://github.com/yourusername/jobboard)

---

## Table of Contents

1. [Goal and Context](#1-goal-and-context)
2. [Target Companies](#2-target-companies)
3. [Tech Stack Decisions](#3-tech-stack-decisions)
4. [Completed — Phase 1: Django Backend](#4-completed--phase-1-django-backend)
5. [In Progress — Week 5: Celery and Async](#5-in-progress--week-5-celery-and-async)
6. [Upcoming — Phase 2: FastAPI](#6-upcoming--phase-2-fastapi)
7. [Upcoming — Phase 3: AI Backend](#7-upcoming--phase-3-ai-backend)
8. [Upcoming — Phase 4: Interview Prep and Applications](#8-upcoming--phase-4-interview-prep-and-applications)
9. [Project: JobBoard API — Full Feature Map](#9-project-jobboard-api--full-feature-map)
10. [Key Technical Decisions Made](#10-key-technical-decisions-made)
11. [Concepts Mastered](#11-concepts-mastered)
12. [Interview Question Bank](#12-interview-question-bank)
13. [Resources Used](#13-resources-used)
14. [Daily Habits and Workflow](#14-daily-habits-and-workflow)
15. [Visa and Japan Logistics](#15-visa-and-japan-logistics)

---

## 1. Goal and Context

**Situation:**  
Currently a student with academic backlogs clearing in October 2026. Degree results come out in January 2027. The goal is to be interview-ready for Japanese backend/AI backend roles starting October 2026 and to have offers by January 2027.

**The strategy:**  
Build a strong enough GitHub portfolio that the transcript doesn't matter. Japanese product companies (Mercari, SmartHR, CyberAgent) evaluate candidates primarily on what they've built and how well they can explain it. A production-grade Django + Celery + Docker project with JWT auth, Redis caching, Swagger docs, and async email tasks is more credible than a clean GPA.

**Why Python over Go:**  
Go is dominant at companies like Mercari and LINE, but Python is the correct choice because:
- The AI/ML ecosystem is entirely Python-first
- Django and FastAPI are explicitly used at SmartHR, freee, CyberAgent AI Lab, Ubie, and MNTSQ
- FastAPI is the standard for AI microservices everywhere
- Having both Django (traditional backend) and FastAPI (AI/async) makes you competitive for two role types simultaneously

---

## 2. Target Companies

| Company | Stack | Role Type | Language |
|---|---|---|---|
| Mercari | Go, Python | Backend | English OK |
| LY Corp (LINE) | Go, Java, Python | Backend | English OK |
| SmartHR | Ruby, Python, Django | Backend, SaaS | English OK |
| freee | Ruby, Python | Backend, SaaS | English OK |
| CyberAgent AI Lab | Python, FastAPI | AI Backend | English OK |
| Ubie | Go, Python | AI Backend, Healthcare | English OK |
| MNTSQ | Python, FastAPI | AI Backend, LegalTech | English OK |
| Wantedly | Go, Ruby | Backend | English OK |
| Recruit (AI division) | Python | AI Backend | English OK |
| Money Forward | Ruby, Python | Backend, Fintech | English OK |

**Job portals to use:**
- Green (外資系・ITエンジニア向け)
- Wantedly
- LinkedIn (international-facing roles)

---

## 3. Tech Stack Decisions

| Decision | Choice | Reason |
|---|---|---|
| Primary language | Python | AI ecosystem, Django+FastAPI breadth |
| Web framework | Django + DRF | Batteries-included, SaaS-standard in Japan |
| Async framework | FastAPI | AI microservices standard, async-native |
| Database | PostgreSQL | Production standard, pgvector for AI phase |
| Cache/Broker | Redis | Industry standard, dual use: cache + Celery |
| Task queue | Celery | Most common in Django ecosystem |
| Containerisation | Docker + Compose | Reproducible environments, shows production thinking |
| Auth | JWT (simplejwt) | API-appropriate, stateless |
| Docs | drf-spectacular | Auto Swagger from code, zero maintenance |
| Testing | pytest + pytest-django | Industry standard for Django |
| CI/CD | GitHub Actions | Free, widely used in Japan startups |
| Deployment | Railway | Simple, Postgres + Redis add-ons free tier |

---

## 4. Completed — Phase 1: Django Backend

### Week 1 — Python Fundamentals
**Status: ✅ Complete**

| Day | Topic | Key Concepts |
|---|---|---|
| 1 | Environment setup | pyenv, venv, VS Code, Git init |
| 2 | OOP deep dive | Classes, inheritance, dunder methods, @property, MRO |
| 3 | Type hints + exceptions | typing module, Optional, Union, dataclasses, context managers |
| 4 | Async Python | async/await, event loop, coroutines, asyncio.gather |
| 5 | Data structures | Comprehensions, generators, itertools |
| 6 | LeetCode practice | 5 easy problems in Python |
| 7 | Review | Gaps identified and addressed |

**Key learnings:**
- Generators: `yield` vs `return` — lazy evaluation
- Async: I/O-bound vs CPU-bound distinction
- `async def` + `await` mental model: worker switches during waits
- Type hints are mandatory in production Python

---

### Week 2 — Django Core: Models, ORM, Admin
**Status: ✅ Complete**

| Day | Topic | Key Concepts |
|---|---|---|
| 1 | Project structure | startproject, startapp, settings.py, INSTALLED_APPS, apps.py |
| 2 | Models and fields | CharField, ForeignKey, ManyToMany, Meta, null vs blank |
| 3 | ORM queries | filter, exclude, get, Q, F, annotate, aggregate, values |
| 4 | N+1 and optimisation | select_related, prefetch_related, Prefetch(), assertNumQueries |
| 5 | Django Admin | ModelAdmin, list_display, inlines, bulk actions |
| 6 | Blog models + 20 ORM queries | Self-referential ForeignKey (comments), shell_plus practice |
| 7 | EXPLAIN ANALYZE | Seq scan vs Index scan vs Bitmap scan, explain.dalibo.com |

**Critical decisions locked in:**
- Always `AUTH_USER_MODEL = 'accounts.User'` before first migration
- `get_or_create` in signals — never `create` (handles duplicates)
- `select_related` for ForeignKey/OneToOne, `prefetch_related` for ManyToMany/reverse FK
- Composite indexes in Meta.indexes for frequent filter+order combinations
- `EXPLAIN ANALYZE` to verify index usage — PostgreSQL ignores indexes for >~20% row returns

**Memorable example — N+1:**
```python
# BAD: 1 + N queries
for job in JobListing.objects.filter(is_active=True):
    print(job.company.name)  # query per job

# GOOD: always 2 queries
for job in JobListing.objects.filter(
    is_active=True
).select_related('company'):
    print(job.company.name)  # no extra query
```

---

### Week 3 — Views, URLs, Forms, Auth, Middleware, Signals
**Status: ✅ Complete**

| Day | Topic | Key Concepts |
|---|---|---|
| 1 | Function-based views + URLs | HttpResponse, JsonResponse, path converters, include(), namespace |
| 2 | Class-based views | View, ListView, DetailView, mixins, LoginRequiredMixin |
| 3 | Django forms + validation | Form, ModelForm, clean(), validate_<field>(), cross-field validation |
| 4 | Django auth system | AbstractUser, authenticate(), login(), logout(), @login_required |
| 5 | Middleware | Request/response lifecycle, custom middleware, process_exception |
| 6 | Django signals | post_save, pre_save, pre_delete, @receiver, AppConfig.ready() |
| 7 | Week review | Full system check, URL verification, commit |

**Critical decisions locked in:**
- `transaction.on_commit` when triggering Celery tasks from signals
- Soft-delete job listings (`is_active=False`) rather than hard-delete
- `pre_save` signal to capture old status before update (for email notifications)
- `AppConfig.ready()` is the correct and only place to connect signals

**Middleware order matters:**
```
SecurityMiddleware
SessionMiddleware          ← loads session
CsrfViewMiddleware
AuthenticationMiddleware   ← needs session loaded first
...your custom middleware  ← needs request.user populated
```

---

### Week 4 — Django REST Framework
**Status: ✅ Complete**

| Day | Topic | Key Concepts |
|---|---|---|
| 1 | DRF setup + serializers | ModelSerializer, nested serializers, read/write split, source=, context |
| 2 | APIView + GenericAPIView | request.data, Response, raise_exception, perform_create, get_queryset |
| 3 | ViewSets + Routers | ModelViewSet, SimpleRouter, @action, self.action, get_permissions |
| 4 | JWT authentication | Access/refresh tokens, custom claims, TokenObtainPairSerializer |
| 5 | Custom permissions | BasePermission, has_permission, has_object_permission, SAFE_METHODS |
| 6 | Filtering + pagination | django-filter, FilterSet, SearchFilter, OrderingFilter, PageNumberPagination |
| 7 | Swagger docs | drf-spectacular, @extend_schema, @extend_schema_view, SpectacularSwaggerView |

**Critical decisions locked in:**
- `SimpleRouter` over `DefaultRouter` when registered with empty prefix
- Separate read and write serializers for JobListing (list vs detail)
- `get_permissions()` per action — not a single class-level `permission_classes`
- `company_id` not required in serializer — server sets from `request.user.company_profile`
- Soft delete in `destroy()` — sets `is_active=False`

**The read/write split pattern:**
```python
class JobListingSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)      # output: full object
    company_id = PrimaryKeyRelatedField(             # input: just the ID
        source='company',
        write_only=True,
        required=False,  # server sets this in perform_create
    )
```

**Permission hierarchy built:**
```
IsCompany           → only company-role users
IsCandidate         → only candidate-role users  
IsCompanyOrReadOnly → GET: anyone, POST/PUT/DELETE: companies only
IsOwnerOrReadOnly   → GET: anyone, write: obj.company.user == request.user
IsAdminOrReadOnly   → GET: anyone, write: admin only
```

**JWT flow:**
```
POST /token/          → returns access (60min) + refresh (7day)
POST /token/refresh/  → returns new access token
Every API request     → Authorization: Bearer <access_token>
Server validates      → mathematical signature check, no DB lookup
```

---

## 5. In Progress — Week 5: Celery and Async

### Week 5 Day 1 — Celery Setup in Docker
**Status: ✅ Complete**

- Celery app created in `jobboard/celery.py`
- Connected to Django via `jobboard/__init__.py`
- Docker Compose updated with `celery` and `flower` services
- `transaction.on_commit` pattern established
- `debug_task` and `add` test tasks verified

**Docker services running:**
```
jobboard_web     → Django API (port 8000)
jobboard_db      → PostgreSQL (port 5432)
jobboard_redis   → Redis broker + cache (port 6379)
jobboard_celery  → Celery worker (concurrency: 2)
jobboard_flower  → Flower monitoring (port 5555)
jobboard_beat    → Celery Beat scheduler
```

---

### Week 5 Day 2 — Email Notification Tasks
**Status: ✅ Complete**

**Tasks built:**

| Task | Trigger | Recipient | When |
|---|---|---|---|
| `send_application_received_email` | post_save (Application, created=True) | Company | New application submitted |
| `send_status_change_email` | post_save (Application, created=False) | Candidate | Status changed |
| `send_welcome_email` | post_save (User, created=True) | New user | After registration |

**Key patterns established:**
```python
# Always use transaction.on_commit to avoid race conditions
transaction.on_commit(
    lambda: send_application_received_email.delay(instance.id)
)

# Always pass IDs to tasks, never model instances
send_email.delay(application.id)  # ✅
send_email.delay(application)     # ❌ can't JSON serialize

# Retry pattern
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def my_task(self, application_id):
    try:
        ...
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

**pre_save to capture old status:**
```python
@receiver(pre_save, sender=Application)
def capture_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except sender.DoesNotExist:
            instance._old_status = None
```

---

### Week 5 Day 3 — Celery Beat (Scheduled Tasks)
**Status: ✅ Complete**

**Scheduled tasks:**

| Task | Schedule | Purpose |
|---|---|---|
| `deactivate_expired_jobs` | Daily midnight (Asia/Tokyo) | Auto-deactivate jobs past deadline |
| `send_weekly_job_digest` | Sundays 9am | Email new jobs to all candidates |
| `remind_unreviewed_applications` | Weekdays 8am | Remind companies with pending apps >3 days |
| `cleanup_stale_cache` | Every hour | Refresh featured_jobs cache |

**Key learnings:**
- Beat runs as a **separate container** — never combine with worker in production
- Never run two Beat instances — tasks get scheduled twice
- `DatabaseScheduler` stores schedules in PostgreSQL — manageable from Django Admin
- Test without waiting: call `task.delay()` directly from shell

---

### Week 5 Day 4 — pytest and Testing
**Status: 🔲 Not started**

**Planned coverage:**

```
tests/
├── accounts/
│   ├── test_registration.py     # candidate + company registration
│   ├── test_jwt.py              # login, refresh, invalid tokens
│   └── test_permissions.py     # role-based access
├── jobs/
│   ├── test_job_listing.py     # CRUD, filtering, pagination
│   ├── test_permissions.py     # owner-only updates
│   └── test_cache.py           # Redis cache hit/miss
├── applications/
│   ├── test_apply.py           # apply, duplicate prevention
│   └── test_status.py          # status change + email trigger
└── conftest.py                 # shared fixtures
```

**Target: 80%+ coverage**

**Key patterns to test:**
- `assertNumQueries(N)` to prove no N+1
- Mock Celery tasks in tests — don't send real emails
- Test permission boundaries: candidate cannot edit a job listing
- Test cache invalidation: update object → cache cleared

---

### Week 5 Day 5 — Application System ViewSet
**Status: 🔲 Not started**

**Planned endpoints:**
```
POST   /api/v1/applications/           # candidate applies to a job
GET    /api/v1/applications/           # candidate sees their applications
GET    /api/v1/applications/{id}/      # detail
PATCH  /api/v1/applications/{id}/      # company changes status
GET    /api/v1/jobs/{id}/applications/ # company sees all applications for their job
```

**Planned permissions:**
```
Create application  → IsCandidate
List own apps       → IsCandidate (only their own)
Change status       → IsCompany (only their jobs)
View applications   → IsCompany (only their jobs' applications)
```

---

### Week 5 Day 6 — GitHub Actions CI/CD
**Status: 🔲 Not started**

**Planned pipeline:**
```yaml
on: [push, pull_request]

jobs:
  test:
    - checkout
    - setup Python
    - install dependencies
    - run PostgreSQL + Redis as services
    - run migrations
    - run pytest with coverage
    - fail if coverage < 80%

  lint:
    - ruff check
    - check no missing migrations
```

---

### Week 5 Day 7 — Deployment to Railway
**Status: 🔲 Not started**

**Planned:**
- Deploy Django app to Railway
- Add PostgreSQL and Redis add-ons
- Configure environment variables
- Set up health check endpoint
- Get live public URL for README
- Update Swagger UI with production URL

---

## 6. Upcoming — Phase 2: FastAPI

### Week 6 — FastAPI Core
**Status: 🔲 Not started**

**Why FastAPI after Django:**
- Django teaches you discipline: models, migrations, security, testing
- FastAPI is async-native and the standard for AI microservices
- Having both makes you competitive for two different role types
- FastAPI knowledge comes naturally after Django — same Python, similar patterns

**Planned topics:**

| Day | Topic |
|---|---|
| 1 | FastAPI setup, routing, Pydantic v2, dependency injection |
| 2 | Async SQLAlchemy 2.0 + Alembic migrations |
| 3 | FastAPI auth — OAuth2, JWT, dependencies |
| 4 | Background tasks, lifespan events, middleware |
| 5 | FastAPI testing with pytest + httpx |
| 6 | Build: URL analytics microservice (two FastAPI services + Kafka) |
| 7 | k6 load testing + Prometheus metrics |

**New project: notification-service**  
A FastAPI microservice that handles WebSocket connections and Server-Sent Events (SSE). Will eventually serve as the real-time layer for the job board — pushing application status updates to clients without polling.

---

## 7. Upcoming — Phase 3: AI Backend

### Week 7 — AI Backend Engineering
**Status: 🔲 Not started**

This is the highest-value phase — what separates a backend candidate from an AI backend candidate. Target companies like CyberAgent AI Lab, Ubie, and MNTSQ specifically need engineers who can build and serve AI features in production.

**Planned topics:**

| Day | Topic |
|---|---|
| 1 | OpenAI API + streaming with FastAPI SSE |
| 2 | RAG pipeline from scratch: chunk → embed → store → retrieve |
| 3 | pgvector setup + vector similarity search |
| 4 | LangChain / LlamaIndex layer on top of raw RAG |
| 5 | Celery for async document ingestion jobs |
| 6 | LLM gateway / proxy service |
| 7 | Semantic search with hybrid BM25 + vector re-ranking |

**New project: document-qa-api**  
A FastAPI service that:
- Accepts PDF uploads
- Chunks and embeds them (OpenAI `text-embedding-3-small`)
- Stores embeddings in pgvector
- Exposes a streaming chat endpoint (SSE)
- Multi-tenant: each user's documents are namespace-isolated
- Celery handles async ingestion
- Redis caches repeated queries

This is exactly what CyberAgent AI Lab and Recruit AI division build internally.

**Key concepts to master:**
- Chunking strategies (RecursiveCharacterTextSplitter, semantic chunking)
- Embedding models (OpenAI, local via Ollama)
- Vector similarity: cosine similarity, HNSW index in pgvector
- RAG retrieval: top-k, MMR (Maximum Marginal Relevance)
- Streaming: `async def` generator + `StreamingResponse`
- Token counting and cost management per API key
- Prompt engineering: system prompts, few-shot examples, chain-of-thought

---

### Week 8 — LLM Gateway and AI Infra
**Status: 🔲 Not started**

**New project: llm-gateway**  
A centralised FastAPI proxy for LLM calls:
- Route to OpenAI / Claude / local Ollama based on request
- Per-API-key token counting
- Cost tracking stored in PostgreSQL
- Per-user rate limiting via Redis
- Full request/response logging
- Automatic fallback on provider failure

This is the kind of internal infrastructure every AI team builds. Knowing it already is a major differentiator.

---

## 8. Upcoming — Phase 4: Interview Prep and Applications

### Week 9 — System Design + LeetCode
**Status: 🔲 Not started**

**System design topics to practice:**

| Design Problem | Relevance |
|---|---|
| Design a job board at LINE scale | Direct relevance to project |
| Design a chat system (LINE/Slack) | WebSocket knowledge |
| Design a recommendation engine | AI backend knowledge |
| Design an LLM chat service at scale | AI backend knowledge |
| Design a URL shortener | Classic, tests caching/DB knowledge |
| Design a notification system | Celery/Redis knowledge |

**Resources:**
- Mercari Engineering Blog (English) — real architecture decisions
- SmartHR Engineering Blog — Django production patterns
- CyberAgent AI Lab Blog — FastAPI + AI infrastructure

**LeetCode targets:**
- Arrays and hashmaps: 20 mediums
- BFS/DFS graphs: 10 mediums
- Binary search: 10 mediums
- Dynamic programming: 5 mediums (good to know, not critical)

---

### Week 10 — Application Season
**Status: 🔲 Not started**

**Pre-application checklist:**
- [ ] All GitHub repos have detailed READMEs with architecture diagrams
- [ ] JobBoard project has live Railway deployment URL
- [ ] Swagger UI accessible at production URL
- [ ] k6 benchmark results in README
- [ ] Loom demo video embedded in README
- [ ] Green.jp profile completed
- [ ] Wantedly profile completed
- [ ] LinkedIn updated with project descriptions

**Application strategy:**
1. Apply via Green and Wantedly first — most Japan-specific
2. LinkedIn for international-facing companies
3. Direct outreach to engineers at target companies after applying
4. Write one Zenn.dev article about RAG architecture or FastAPI streaming — Japanese engineers will find it

---

## 9. Project: JobBoard API — Full Feature Map

### Completed features

```
Architecture
  ✅ Multi-app Django project (accounts, jobs, applications, blog, notifications)
  ✅ Custom User model with roles (company / candidate / admin)
  ✅ Docker Compose: web + PostgreSQL + Redis + Celery + Flower + Beat
  ✅ Seed management command (python manage.py seed_data --clear)

Database
  ✅ Full schema: User, CompanyProfile, CandidateProfile, JobListing, 
     Application, Category, Tag, Post, Comment
  ✅ Composite indexes (is_active + posted_at, salary_min)
  ✅ Self-referential ForeignKey (Comment.parent)
  ✅ Soft-delete pattern (is_active=False)

API
  ✅ JWT auth with custom claims (role, username, email in token)
  ✅ Role-based permissions (IsCompany, IsCandidate, IsOwnerOrReadOnly)
  ✅ ViewSet with Router + custom @action endpoints (featured, similar)
  ✅ django-filter FilterSet (location, job_type, salary range, remote, category)
  ✅ SearchFilter (title, description, company name)
  ✅ OrderingFilter (salary, date, title)
  ✅ Custom pagination (total_pages, current_page, page_size query param)
  ✅ Swagger UI at /api/schema/swagger-ui/
  ✅ ReDoc at /api/schema/redoc/

Performance
  ✅ select_related + prefetch_related (N+1 free)
  ✅ Redis cache: categories (1hr TTL), job detail (30min), featured (1hr)
  ✅ Signal-based cache invalidation (post_save/post_delete → cache.delete)
  ✅ EXPLAIN ANALYZE verified index usage

Admin
  ✅ Custom ModelAdmin for all models
  ✅ Bulk actions (activate/deactivate jobs, change application status)
  ✅ Inline: JobListings inside CompanyProfile
  ✅ Custom job count annotation on CompanyProfileAdmin
  ✅ list_select_related to prevent N+1 in admin list views

Middleware
  ✅ RequestLoggerMiddleware (method, path, status, timing, user)
  ✅ RoleAuditMiddleware (role-based access logging)
  ✅ MaintenanceModeMiddleware (503 with MAINTENANCE_MODE setting)
  ✅ JsonExceptionMiddleware (JSON error responses for API endpoints)

Signals
  ✅ Auto-create CandidateProfile on User post_save
  ✅ Application notifications (new application, status change)
  ✅ Job listing change logging
  ✅ Cache invalidation on Category and JobListing changes

Async / Celery
  ✅ send_application_received_email (company notified on new application)
  ✅ send_status_change_email (candidate notified on status change)
  ✅ send_welcome_email (new user registration)
  ✅ deactivate_expired_jobs (nightly Beat task)
  ✅ send_weekly_job_digest (Sunday Beat task)
  ✅ remind_unreviewed_applications (weekday Beat task)
  ✅ cleanup_stale_cache (hourly Beat task)
  ✅ Flower monitoring at port 5555
  ✅ transaction.on_commit pattern throughout
  ✅ max_retries=3 with countdown=60 on all email tasks
```

### Remaining features

```
  🔲 Application system ViewSet (apply, track, status change via API)
  🔲 pytest test suite (80%+ coverage)
  🔲 assertNumQueries tests for N+1 proof
  🔲 GitHub Actions CI pipeline
  🔲 Railway deployment (live public URL)
  🔲 k6 load test results in README
  🔲 Loom demo video
```

---

## 10. Key Technical Decisions Made

These decisions should be referenced when explaining the project in interviews. Every one has a reason.

| Decision | Why |
|---|---|
| `settings.AUTH_USER_MODEL` in non-accounts apps | Avoids circular imports, decoupled design |
| Custom User model before first migration | Cannot be changed without destroying migrations |
| `get_or_create` in signals | Handles edge cases where profile already exists |
| `transaction.on_commit` with Celery | Worker might run before DB transaction commits |
| Soft-delete (`is_active=False`) | Applications reference jobs — hard delete breaks data |
| `SimpleRouter` over `DefaultRouter` | Empty prefix registration conflicts with API root page |
| Separate read/write serializers | List views need lightweight responses, detail needs full data |
| `pre_save` to capture old status | `post_save` doesn't expose previous values |
| `propagate: False` in logging config | Prevents Celery root handler duplicating log lines |
| `required=False` on `company_id` serializer field | Server sets company from request.user in perform_create |
| Per-action `get_permissions()` | Different actions need different permissions on same ViewSet |
| Beat as separate Docker container | Prevents double-scheduling if worker crashes |
| `bulk_create` for seed data | One INSERT for 200 rows vs 200 individual INSERTs |

---

## 11. Concepts Mastered

### Django

- **ORM:** filter, exclude, get, Q, F, annotate, aggregate, values, values_list, iterator, bulk_create, bulk_update
- **Relationships:** ForeignKey, OneToOneField, ManyToManyField, self-referential FK, through models
- **Optimisation:** select_related (JOIN), prefetch_related (separate query + Python join), Prefetch() with to_attr
- **Migrations:** makemigrations, migrate, squashmigrations, data migrations, RunSQL
- **Admin:** ModelAdmin, TabularInline, StackedInline, list_select_related, custom actions, get_queryset override
- **Auth:** AbstractUser, authenticate(), login(), logout(), @login_required, UserPassesTestMixin
- **Signals:** post_save, pre_save, pre_delete, post_delete, m2m_changed, AppConfig.ready()
- **Forms:** Form, ModelForm, clean(), validate_<field>(), commit=False, save_m2m()
- **Middleware:** __call__ pattern, process_exception hook, request/response lifecycle
- **Cache:** cache.get/set/delete/clear, timeout, cache invalidation strategy
- **Management commands:** BaseCommand, handle(), add_arguments(), @transaction.atomic

### DRF

- **Serializers:** ModelSerializer, SerializerMethodField, nested, read_only, write_only, source, context, validate()
- **Views:** APIView, GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
- **ViewSets:** ModelViewSet, ReadOnlyModelViewSet, @action, self.action, get_permissions(), get_serializer_class()
- **Routers:** SimpleRouter, DefaultRouter, register(), basename
- **Auth:** JWTAuthentication, TokenObtainPairView, custom claims via get_token()
- **Permissions:** BasePermission, has_permission, has_object_permission, SAFE_METHODS
- **Filtering:** DjangoFilterBackend, FilterSet, lookup_expr, SearchFilter, OrderingFilter
- **Pagination:** PageNumberPagination, CursorPagination, page_size_query_param, max_page_size
- **Docs:** drf-spectacular, @extend_schema, @extend_schema_view, SpectacularSwaggerView

### Celery

- **Core:** @shared_task, bind=True, delay(), apply_async(), task states (PENDING/STARTED/SUCCESS/FAILURE)
- **Reliability:** max_retries, default_retry_delay, self.retry(), countdown, CELERY_ACKS_LATE
- **Beat:** crontab, timedelta schedules, DatabaseScheduler, django-celery-beat
- **Patterns:** transaction.on_commit, pass IDs not objects, idempotent tasks
- **Monitoring:** Flower dashboard, task history, worker status

### PostgreSQL

- **Indexes:** B-tree (default), GIN (full-text, jsonb), composite indexes, partial indexes
- **EXPLAIN ANALYZE:** Seq Scan vs Index Scan vs Bitmap Heap Scan
- **Full-text search:** SearchVector, SearchQuery, SearchRank, GIN index
- **Query tuning:** EXPLAIN ANALYZE, explain.dalibo.com visualiser
- **Connection:** psycopg2, pgBouncer concept, CONN_MAX_AGE

### Redis

- **Data types:** String, Hash, List, Set, Sorted Set
- **Commands:** GET, SET, DEL, EXPIRE, TTL, KEYS, FLUSHDB
- **Django integration:** django-redis, CACHES config, cache.get/set/delete
- **Celery integration:** broker + result backend, database separation (db/0 vs db/1)
- **Cache invalidation:** signal-based deletion, TTL-based expiry

### Docker

- **Dockerfile:** FROM, WORKDIR, ENV, COPY, RUN, EXPOSE, CMD
- **Layer caching:** requirements.txt before code copy
- **Docker Compose:** services, volumes, depends_on with healthcheck, networks
- **Commands:** up --build, down -v, exec, logs -f, restart, ps
- **Networking:** service name as hostname (DB_HOST=db not localhost)

---

## 12. Interview Question Bank

### Django

**Q: How do you prevent N+1 queries?**  
Use `select_related` for ForeignKey/OneToOne (SQL JOIN) and `prefetch_related` for ManyToMany/reverse FK (separate query, Python join). Use `assertNumQueries` in tests to prove the count stays constant. Use `django-debug-toolbar` in development to spot them.

**Q: Where do you connect signals and why?**  
`AppConfig.ready()` in `apps.py`. It's called once when Django fully loads. Connecting in `models.py` causes duplicate signal connections because the file can be imported multiple times.

**Q: What is the difference between null=True and blank=True?**  
`null=True` is a database constraint — the column can store NULL. `blank=True` is a validation constraint — the field is not required in forms/serializers. For text fields use only `blank=True` (avoid two empty states: NULL and ''). For numbers and dates use `null=True, blank=True`.

**Q: Why use soft delete instead of hard delete?**  
Applications reference job listings. Hard-deleting a job would either cascade-delete all applications (data loss) or leave orphaned foreign keys. Soft delete preserves referential integrity, audit trails, and analytics data.

### DRF

**Q: What is the difference between has_permission and has_object_permission?**  
`has_permission` runs on every request — view-level check. `has_object_permission` runs only when `get_object()` is called — object-level check. You need both because `has_permission` doesn't have the specific object yet.

**Q: Why have two serializers for JobListing?**  
List views return 20 jobs and don't need the full description or nested objects — a lightweight serializer reduces payload from ~50KB to ~5KB. Detail views need the full data. Two serializers = performance optimisation with no extra effort.

**Q: How does JWT authentication work?**  
Login returns access token (60min) and refresh token (7 days). Every request sends access token in Authorization header. Server verifies the cryptographic signature — no database lookup needed. When access token expires, client sends refresh token to get a new one.

### Celery

**Q: Why transaction.on_commit?**  
Signals fire inside the database transaction. Without on_commit, Celery might pick up the task before the transaction commits — the worker queries the DB and finds nothing. on_commit delays dispatch until after commit.

**Q: Why pass IDs to tasks not model instances?**  
Tasks are serialized to JSON for Redis storage. Model instances can't be JSON serialized. Also the object might change between signal and task execution — fetching fresh from DB inside the task guarantees the latest data.

**Q: What is the difference between Beat and Worker?**  
Beat is a scheduler — it only queues tasks at the right time. Worker executes tasks from the queue. They must run as separate processes. Never run two Beat instances — tasks get scheduled twice.

---

## 13. Resources Used

### Free

| Resource | Used For |
|---|---|
| Django official docs | Models, ORM, Admin, auth, cache |
| DRF official docs | Serializers, views, permissions |
| Classy DRF (cdrf.co) | Visual CBV/ViewSet reference |
| TestDriven.io articles | DRF, Celery, Docker, testing |
| Real Python | Python internals, async, type hints |
| use-the-index-luke.com | PostgreSQL indexes, EXPLAIN ANALYZE |
| explain.dalibo.com | Visual EXPLAIN ANALYZE output |
| Redis University RU101 | Redis data types |
| Celery docs | Canvas (chains/chords/groups), Beat |
| pytest-django docs | Testing patterns |
| drf-spectacular docs | OpenAPI customisation |
| dbdiagram.io | ER diagram generation |
| Mailtrap.io | Fake SMTP for email testing |

### Paid (worth it)

| Resource | Cost | Used For |
|---|---|---|
| Django for APIs (learndjango.com) | ~$10 | DRF fundamentals |
| Two Scoops of Django | ~$40 | Best practices, settings, model design |

---

## 14. Daily Habits and Workflow

### Every study session

1. Pull latest code: `git pull`
2. Start Docker: `docker-compose up -d`
3. Study/build the day's topic
4. Test in Postman or browser
5. Commit with conventional message: `git commit -m "feat: add ..."`
6. Push: `git push`

### Conventional commit format

```
feat:     new feature
fix:      bug fix
docs:     documentation change
chore:    maintenance (deps, config)
test:     adding tests
refactor: code change that isn't a fix or feature
perf:     performance improvement
```

### Docker daily commands

```powershell
docker-compose up -d              # start in background
docker-compose logs -f web        # follow web logs
docker-compose logs -f celery     # follow celery logs
docker-compose exec web python manage.py shell_plus
docker-compose exec web python manage.py seed_data
docker-compose restart web        # after settings changes
docker-compose down               # stop everything
docker-compose down -v            # stop + delete volumes (fresh DB)
```

---

## 15. Visa and Japan Logistics

**Target visa:** Engineer / Specialist in Humanities visa  
**Requirements:** Relevant degree (CS/Engineering) OR 10 years experience

**Timeline concern:**  
Backlogs clear October 2026, degree results January 2027. Strategy: be upfront with companies about the January result date. Many Japanese startups have handled this before. Strong GitHub work makes the conversation easier.

**Points to know:**  
The Highly Skilled Professional (HSP) visa has a points system. A degree + job offer + age under 30 typically scores enough for expedited processing (70+ points). Worth researching once an offer is in hand.

**Application timeline:**
```
Oct 2026  → Backlogs clear, start full-time applications
            Target: 10 applications per week on Green + Wantedly
Nov 2026  → Interview season begins
Dec 2026  → Final rounds + offer negotiation
Jan 2027  → Degree results shared with sponsor company
            CoE (Certificate of Eligibility) application timing discussion
```

**Salary benchmarks (Tokyo, 2026):**
```
Entry backend engineer:       ¥4M – ¥6M/year
Mid-level Python/AI backend:  ¥6M – ¥9M/year
Strong candidate (portfolio): ¥7M – ¥12M/year
```

---

## Progress Tracker

| Phase | Status | Completion |
|---|---|---|
| Week 1: Python fundamentals | ✅ Complete | 100% |
| Week 2: Django core | ✅ Complete | 100% |
| Week 3: Views, auth, middleware, signals | ✅ Complete | 100% |
| Week 4: DRF, JWT, permissions, Swagger | ✅ Complete | 100% |
| Week 5 Day 1: Celery setup | ✅ Complete | 100% |
| Week 5 Day 2: Email tasks | ✅ Complete | 100% |
| Week 5 Day 3: Celery Beat | ✅ Complete | 100% |
| Week 5 Day 4: pytest | 🔲 Not started | 0% |
| Week 5 Day 5: Application ViewSet | 🔲 Not started | 0% |
| Week 5 Day 6: GitHub Actions | 🔲 Not started | 0% |
| Week 5 Day 7: Railway deployment | 🔲 Not started | 0% |
| Week 6: FastAPI | 🔲 Not started | 0% |
| Week 7: AI Backend (RAG, LLMs) | 🔲 Not started | 0% |
| Week 8: LLM Gateway + AI Infra | 🔲 Not started | 0% |
| Week 9: System design + LeetCode | 🔲 Not started | 0% |
| Week 10: Applications + interviews | 🔲 Not started | 0% |

---

*Last updated: June 2026*  
*Reference this file at the start of each week to stay on track.*  
*Update the progress tracker after completing each day.*
