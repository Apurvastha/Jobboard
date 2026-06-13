import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import CandidateProfile, CompanyProfile

User = get_user_model()


@pytest.mark.django_db
class TestRegistration:

    def test_candidate_registration(self, api_client):
        """Candidate can register — profile auto-created via signal."""
        response = api_client.post('/api/v1/accounts/register/candidate/', {
            'username': 'newcandidate',
            'email': 'newcandidate@test.com',
            'password': 'testpass123!',
            'password2': 'testpass123!',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['role'] == 'candidate'

        user = User.objects.get(username='newcandidate')
        assert user.is_candidate is True
        # signal should have auto-created the profile
        assert CandidateProfile.objects.filter(user=user).exists()

    def test_company_registration(self, api_client):
        """Company can register — company profile created."""
        response = api_client.post('/api/v1/accounts/register/company/', {
            'username': 'newcompany',
            'email': 'newcompany@test.com',
            'password': 'testpass123!',
            'password2': 'testpass123!',
            'company_name': 'New Company Ltd',
            'country': 'Japan',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['role'] == 'company'

        user = User.objects.get(username='newcompany')
        assert CompanyProfile.objects.filter(user=user).exists()
        assert user.company_profile.name == 'New Company Ltd'

    def test_password_mismatch_rejected(self, api_client):
        """Mismatched passwords fail validation."""
        response = api_client.post('/api/v1/accounts/register/candidate/', {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'testpass123!',
            'password2': 'differentpass!',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_username_rejected(self, api_client, candidate_user):
        """Duplicate username fails validation."""
        response = api_client.post('/api/v1/accounts/register/candidate/', {
            'username': 'testcandidate',  # same as fixture
            'email': 'different@test.com',
            'password': 'testpass123!',
            'password2': 'testpass123!',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProfileEndpoints:

    def test_candidate_can_view_own_profile(self, candidate_client):
        response = candidate_client.get('/api/v1/accounts/profile/candidate/')
        assert response.status_code == status.HTTP_200_OK

    def test_company_cannot_view_candidate_profile(self, company_client):
        response = company_client.get('/api/v1/accounts/profile/candidate/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_candidate_can_update_profile(self, candidate_client):
        response = candidate_client.patch(
            '/api/v1/accounts/profile/candidate/',
            {'bio': 'Backend engineer targeting Japan.', 'years_of_experience': 2},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['bio'] == 'Backend engineer targeting Japan.'

    def test_company_can_view_own_profile(self, company_client):
        response = company_client.get('/api/v1/accounts/profile/company/')
        assert response.status_code == status.HTTP_200_OK

    def test_candidate_cannot_view_company_profile(self, candidate_client):
        response = candidate_client.get('/api/v1/accounts/profile/company/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_company_can_update_profile(self, company_client):
        response = company_client.patch(
            '/api/v1/accounts/profile/company/',
            {'description': 'Leading tech company in Tokyo.'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestJWT:

    def test_login_returns_tokens(self, api_client, candidate_user):
        """Login returns access and refresh tokens."""
        response = api_client.post('/api/v1/accounts/token/', {
            'username': 'testcandidate',
            'password': 'testpass123!',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_returns_custom_claims(self, api_client, candidate_user):
        """Login response includes role, username, email."""
        response = api_client.post('/api/v1/accounts/token/', {
            'username': 'testcandidate',
            'password': 'testpass123!',
        }, format='json')
        assert response.data['role'] == 'candidate'
        assert response.data['username'] == 'testcandidate'
        assert response.data['email'] == 'candidate@test.com'

    def test_wrong_password_rejected(self, api_client, candidate_user):
        """Wrong password returns 401."""
        response = api_client.post('/api/v1/accounts/token/', {
            'username': 'testcandidate',
            'password': 'wrongpassword',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_requires_authentication(self, api_client):
        """GET /me/ without token returns 401."""
        response = api_client.get('/api/v1/accounts/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_returns_user_data(self, candidate_client, candidate_user):
        """GET /me/ returns correct user data."""
        response = candidate_client.get('/api/v1/accounts/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testcandidate'
        assert response.data['role'] == 'candidate'
        # password should never be in response
        assert 'password' not in response.data