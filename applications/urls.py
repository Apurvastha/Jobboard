from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register("", views.ApplicationViewSet, basename="application")

app_name = "applications"

urlpatterns = [path("", include(router.urls))]
