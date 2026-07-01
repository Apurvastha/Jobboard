import os
import sys
from datetime import timedelta
from pathlib import Path
import environ
from celery.schedules import crontab
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration



BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

# ── SECURITY ──────────────────────────────────────────────────
SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# ── APPLICATIONS ──────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third party
    'django_extensions',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    'django_celery_beat',
    # local apps
    'accounts.apps.AccountsConfig',
    'jobs.apps.JobsConfig',
    'applications.apps.ApplicationsConfig',
    'notifications.apps.NotificationsConfig',
    'blog.apps.BlogConfig',
]

# ── MIDDLEWARE ────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'jobboard.middleware.RequestLoggerMiddleware',
    'jobboard.middleware.MaintenanceModeMiddleware',
    'jobboard.middleware.RoleAuditMiddleware',
    'jobboard.middleware.JsonExceptionMiddleware',
]

ROOT_URLCONF = 'jobboard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jobboard.wsgi.application'

# ── DATABASE ──────────────────────────────────────────────────
DATABASE_URL = env('DATABASE_URL', default=None)

if DATABASE_URL:
    # production — Railway provides DATABASE_URL automatically
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # local development — Docker Compose
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='jobboard_db'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': env('DB_PASSWORD', default='postgres'),
            'HOST': env('DB_HOST', default='db'),
            'PORT': env('DB_PORT', default='5432'),
        }
    }

# ── REDIS ─────────────────────────────────────────────────────
REDIS_URL = env('REDIS_URL', default='redis://127.0.0.1:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

# ── AUTH ──────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── DRF ───────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'accounts.authentication.RedisRevokedJWTAuthentication'
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter'
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ],
    'DEFAULT_THROTTLE_CLASSES': [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',    # unauthenticated users
        'user': '1000/day',   # authenticated users
        'login': '5/minute'
    }

}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ── SPECTACULAR ───────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'JobBoard API',
    'DESCRIPTION': '''
A production-ready job board REST API built with Django and DRF.

## Quick Start

**Step 1 — Get a token:**

POST to `/api/v1/accounts/token/` with one of these test accounts:

| Role | Username | Password |
|---|---|---|
| Candidate | `alice` | `testpass123` |
| Company | `mercari` | `testpass123` |

**Step 2 — Authorize:**

Click the **Authorize** button (top right 🔒), paste the `access` token, click Authorize.

**Step 3 — Explore:**

- As **candidate** → apply to jobs, view your applications
- As **company** → create jobs, review applications, change status

---

## Features

- JWT authentication with token rotation and blacklisting
- Role-based permissions (company / candidate / admin)
- Job listings with filtering, search, and pagination
- Async email notifications via Celery
- Redis caching with signal-based invalidation
- 66 pytest tests · 86% coverage

## Source Code

[github.com/Apurvastha/jobboard](https://github.com/Apurvastha/jobboard)
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
        'displayRequestDuration': True,
        'filter': True,
    },
    'SECURITY': [{'bearerAuth': []}],
    'COMPONENTS': {
        'securitySchemes': {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}

# ── CELERY ────────────────────────────────────────────────────
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Asia/Tokyo'
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60
CELERY_TASK_ACKS_LATE = True
CELERY_RESULT_EXPIRES = 86400
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CELERY_BEAT_SCHEDULE = {
    'deactivate-expired-jobs': {
        'task': 'jobs.tasks.deactivate_expired_jobs',
        'schedule': crontab(hour=0, minute=0),
    },
    'weekly-job-digest': {
        'task': 'jobs.tasks.send_weekly_job_digest',
        'schedule': crontab(hour=9, minute=0, day_of_week='sunday'),
    },
    'remind-unreviewed-application': {
        'task': 'applications.tasks.remind_unreviewed_applications',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday-friday'),
    },
    'cleanup-cache': {
        'task': 'jobs.tasks.cleanup_stale_cache',
        'schedule': crontab(minute=0),
    },
    'celery-backend-cleanup': {
        'task': 'celery.backend_cleanup',
        'schedule': crontab(minute=0, hour='*/1'),
    }
}

# ── SENTRY ─────────────────────────────────────────────────────
SENTRY_DSN = env('SENTRY_DSN', default='')

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True
            ),
            CeleryIntegration(
                monitor_beat_tasks=True
            ),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        sample_rate=1.0,
        environment=env('SENTRY_ENVIRONMENT', default='production'),
        release=env('RAILWAY_GIT_COMMIT_SHA', default='local'),
        send_default_pii=False,
        attach_stacktrace=True
    )

# ── EMAIL ─────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='sandbox.smtp.mailtrap.io')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@jobboard.com')
EMAIL_TIMEOUT = 5 # seconds

# ── STATIC FILES ──────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── INTERNATIONALISATION ──────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── MAINTENANCE MODE ──────────────────────────────────────────
MAINTENANCE_MODE = False

# ── SECURITY HEADERS ───────────────────────────────────────────────────
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = False # railway handles this - no need for redirect
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
SILENCED_SYSTEM_CHECKS = ['security.W008'] # ssl handled by railway proxy


# ── LOGGING ───────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'jobboard.middleware': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts.signals': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'applications.signals': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'applications.tasks': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'jobs.signals': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

if 'pytest' in sys.modules:
    REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

if os.environ.get('DISABLE_THROTTLING') == 'true':
    REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}