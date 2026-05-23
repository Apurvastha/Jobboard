from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('<int:pk>/', views.job_detail, name='detail'),
    path('category/<slug:slug>/', views.jobs_by_category, name='by_category'),
]