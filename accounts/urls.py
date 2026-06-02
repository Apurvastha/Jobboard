from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    #auth
    path('register/candidate/', views.RegisterCandidateView.as_view(), name = 'register_candiate'),
    path('register/company/', views.RegisterCompanyView.as_view(), name = 'register_company'),
  
    #profile
    path('me/', views.MeView.as_view(), name = 'me'),
    path('profile/candidate/', views.CandidateProfileView.as_view(), name = 'candidate_profile'),
    path('profile/company/', views.CompanyProfileView.as_view(), name = 'company_profile'),

]