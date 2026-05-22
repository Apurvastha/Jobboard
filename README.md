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

- [x] Multi-app architecture (accounts, jobs, applications, blog, notifications)
- [x] Custom User model with roles (company / candidate / admin)
- [x] Job listing, application, blog, and company models with full schema design
- [x] Database indexes for query optimisation (composite, single-column)
- [x] Django Admin configured for all models with bulk actions and inlines
- [x] Query optimisation with select_related and prefetch_related (N+1 free)
- [x] EXPLAIN ANALYZE query plan analysis
- [ ] JWT authentication with role-based permissions
- [ ] Job listing CRUD with filtering and full-text search
- [ ] Application system with status tracking
- [ ] Async email notifications via Celery
- [ ] REST API with Swagger / OpenAPI docs
- [ ] 80%+ test coverage with pytest
- [ ] Dockerized with docker-compose
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Deployed to Railway

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
DJANGO_SECRET_KEY=
DEBUG=True
DB_NAME=jobboard_db
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```
## Project Status

Actively in development. New features added regularly.