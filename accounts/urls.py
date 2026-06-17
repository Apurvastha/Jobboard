from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema
from . import views

TokenRefreshView = extend_schema(
    tags=['Authentication'],
    summary='Refresh access token',
    description='Send a refresh token to get a new access token without logging in again.',
)(TokenRefreshView)

app_name = "accounts"

urlpatterns = [
    # registration
    path("register/candidate/",views.RegisterCandidateView.as_view(),name="register_candiate"),
    path("register/company/",views.RegisterCompanyView.as_view(),name="register_company"),

    # JWT auth - login and refresh
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain"),  # login
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # refresh
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # profile
    path("me/", views.MeView.as_view(), name="me"),
    path("profile/candidate/",views.CandidateProfileView.as_view(),name="candidate_profile",),
    path("profile/company/", views.CompanyProfileView.as_view(), name="company_profile"),
]
