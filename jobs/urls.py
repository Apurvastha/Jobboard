from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'jobs'

router = DefaultRouter()
router.register('', views.JobListingViewSet, basename='job')

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('', include(router.urls)),
    


    
]