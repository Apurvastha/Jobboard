"""
URL configuration for jobboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.db import connection
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

admin.site.site_header = "JobBoard Admin"
admin.site.site_title = "JobBoard"
admin.site.index_title = "Dashboard"

def health_check(request):
    try:
        connection.ensure_connection()
        db_status = 'ok'
    except Exception:
        db_status = 'error'
    return JsonResponse({
        'status': 'ok',
        'database': db_status
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path('health/', health_check, name = 'health'),
    # API endpoints
    path("api/v1/jobs/", include("jobs.urls", namespace="jobs")),
    path("api/v1/accounts/", include("accounts.urls", namespace="accounts")),
    path(
        "api/v1/applications/", include("applications.urls", namespace="applications")
    ),
    # OpenAPI schema - raw JSON/YAML
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI - visual interactive docs
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # ReDoc - alternative clean docs UI
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
