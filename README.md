# JobBoard API

A production-ready job board REST API built with Django and Django REST Framework.

## Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Database:** PostgreSQL
- **Cache & Queue:** Redis, Celery
- **Docs:** Swagger / OpenAPI (drf-spectacular)
- **CI/CD:** GitHub Actions
- **Deployment:** Railway

## Features

## Features

- [x] Multi-app architecture (accounts, jobs, applications, blog, notifications)
- [x] Custom User model with roles (company / candidate / admin)
- [x] Job listing, application, blog, and company models with full schema design
- [x] Database indexes for query optimisation (composite, single-column)
- [x] Django Admin configured for all models with bulk actions and inlines
- [x] Query optimisation with select_related and prefetch_related (N+1 free)
- [x] EXPLAIN ANALYZE query plan analysis
- [x] Function-based and class-based views with filtering
- [x] Form validation for search and job creation
- [x] Auth system — registration, login, logout, role-based access
- [x] Custom middleware — request logging, audit trail, error handling
- [x] Signals — auto profile creation, application notifications
- [ ] JWT authentication with role-based permissions (Week 4)
- [ ] DRF serializers and viewsets (Week 4)
- [ ] Job listing CRUD with filtering and full-text search (Week 4)
- [ ] Application system with status tracking (Week 4)
- [ ] Async email notifications via Celery (Week 5)
- [ ] REST API with Swagger / OpenAPI docs (Week 4)
- [ ] 80%+ test coverage with pytest (Week 7)
- [ ] Dockerized with docker-compose (Week 6)
- [ ] CI/CD pipeline with GitHub Actions (Week 6)
- [ ] Deployed to Railway (Week 8)

## Database Schema

## Database Schema

**JobBoard Schema**
![JobBoard Schema](docs/jobboard_schema.png)

**Blog Schema**
![Blog Schema](docs/blog_schema.png)

## Project Structure

```
jobboard/
├── accounts/
├── jobs/
├── applications/
├── blog/
├── notifications/
└── docs/
    └── jobboard_schema.png  ← jobs, accounts, applications
    └── blog_schema.png      ← blog posts, comments, tags
```
## Local Setup

```bash
git clone https://github.com/yourusername/jobboard.git
cd jobboard
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # fill in your values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` to access the admin panel.

## Environment Variables
```
DJANGO_SECRET_KEY= your_secret_key
DEBUG=True
DB_NAME=jobboard_db
DB_USER=postgres
DB_PASSWORD= your_password
DB_HOST=localhost
DB_PORT=5432
```
## Project Status

Actively in development. New features added regularly.