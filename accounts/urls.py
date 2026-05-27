from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    #auth
    path('register/candidate/', views.register_candidate, name = 'register_candiate'),
    path('register/company/', views.register_company, name = 'register_company'),
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout_view, name = 'logout'),

    #profile
    path('me/', views.me, name = 'me'),
    path('profile/candidate/', views.UpdateCandidateProfileView.as_view(), name = 'candidate_profile'),
    path('profile/company/', views.UpdateCompanyProfileView.as_view(), name = 'company_profile'),

]