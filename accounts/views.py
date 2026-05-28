import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .forms import(
    CandidateRegistrationForm,
    CompanyRegistrationForm,
    LoginForm,
    CandidateProfileForm,
    CompanyProfileForm,
)
from .models import User


# --- REGISTRATION --------------------------------------------------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(['POST'])
def register_candidate(request):
    data = json.loads(request.body)
    form = CandidateRegistrationForm(data)

    if form.is_valid():
        user = form.save()
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.id,
        }, status = 201)
    return JsonResponse({'errors: form.errors'}, status = 400)

@csrf_exempt
@require_http_methods(['POST'])
def register_company(request):
    data = json.loads(request.body)
    form = CompanyRegistrationForm(data)

    if form.is_valid():
        user = form.save()
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'company': user.company_profile.name,
        }, status = 201)
    return JsonResponse({'errors': form.errors}, status = 400)


#-----LOGIN / LOGOUT ---------------------------------------------------------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(['POST'])
def login_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    # authenticate checks username + password against DB
    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse(
            {'error': 'Invalid username or password.'},
            status = 401
        )
    
    if not user.is_active:
        return JsonResponse(
            {'error': 'This account has been deactivated.'},
            status = 401
        )
    
    # login creates a session and sets the session cookie
    login(request, user)

    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
    })

@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully.'})


#---PROFILE-----------------------------------------------------------------------------------------------------------------------------

@login_required
@require_http_methods(['GET'])
def me(request):
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat(),
    }
    if user.is_company and user.has_company_profile:
        profile = user.company_profile
        data['company_profile'] = {
            'id': profile.id,
            'name': profile.name,
            'website': profile.website,
            'country': profile.country,
        }
    
    if user.is_candidate and user.has_candidate_profile:
        profile = user.candiate_profile
        data['candidate_profile'] = {
            'id': profile.id,
            'bio': profile.bio,
            'years_of_experience': profile.years_of_experience,
            'skills': profile.skills,
        }
    return JsonResponse(data)


#------PROFILE UPDATE ----------------------------------------------------------------------------------------------------------------------------

class UpdateCandidateProfileView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        # only candidates can update candidate profile
        return self.request.user.is_candidate
    
    def get(self, request):
        if not request.user.has_candidate_profile:
            return JsonResponse({'error': 'Profile not found.'}, status = 404)
        
        profile = request.user.candidate_profile
        return JsonResponse({
            'bio': profile.bio,
            'resume_url': profile.resume_url,
            'years_of_experience': profile.years_of_experience,
            'skills': profile.skills,
        })
    
    def post(self, request):
        data = json.loads(request.body)

        # get or create profile
        profile, created = request.user.__class__._default_manager\
            .get_or_create_candidate_profile(request.user)
        
        from .models import CandidateProfile
        profile, created = CandidateProfile.objects.get_or_create(
            user=request.user
        )

        form = CandidateProfileForm(data, instance=profile)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Profile updated.'})

        return JsonResponse({'errors': form.errors}, status=400)


class UpdateCompanyProfileView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_company

    def get(self, request):
        if not request.user.has_company_profile:
            return JsonResponse({'error': 'Profile not found.'}, status=404)

        profile = request.user.company_profile
        return JsonResponse({
            'name': profile.name,
            'website': profile.website,
            'description': profile.description,
            'country': profile.country,
            'founded_year': profile.founded_year,
        })

    def post(self, request):
        data = json.loads(request.body)
        profile = request.user.company_profile
        form = CompanyProfileForm(data, instance=profile)

        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Profile updated.'})

        return JsonResponse({'errors': form.errors}, status=400)