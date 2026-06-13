from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register('', views.ApplicationViewSet, basename='application')

app_name = 'applications'

urlpatterns = [
    path('', include(router.urls))
]