from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.JobListView.as_view(), name='list'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='detail'),
    path('category/<slug:slug>/', views.JobsByCategoryView.as_view(), name='by_category'),


    path('broken/', views.broken_view, name='broken'),
]