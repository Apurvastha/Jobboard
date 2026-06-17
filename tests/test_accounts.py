import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from accounts.models import CandidateProfile, CompanyProfile

User = get_user_model()


@pytest.mark.django_db
class TestRegistration:
    def test_candidate_registration(self, api_client):
        """Candidate can register — profile auto-created via signal."""
        response = api_client.post(
            "/api/v1/accounts/register/candidate/",
            {
                "username": "newcandidate",
                "email": "newcandidate@test.com",
                "password": "testpass123!",
                "password2": "testpass123!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["role"] == "candidate"

        user = User.objects.get(username="newcandidate")
        assert user.is_candidate is True
        # signal should have auto-created the profile
        assert CandidateProfile.objects.filter(user=user).exists()

    def test_company_registration(self, api_client):
        """Company can register — company profile created."""
        response = api_client.post(
            "/api/v1/accounts/register/company/",
            {
                "username": "newcompany",
                "email": "newcompany@test.com",
                "password": "testpass123!",
                "password2": "testpass123!",
                "company_name": "New Company Ltd",
                "country": "Japan",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["role"] == "company"

        user = User.objects.get(username="newcompany")
        assert CompanyProfile.objects.filter(user=user).exists()
        assert user.company_profile.name == "New Company Ltd"

    def test_password_mismatch_rejected(self, api_client):
        """Mismatched passwords fail validation."""
        response = api_client.post(
            "/api/v1/accounts/register/candidate/",
            {
                "username": "testuser",
                "email": "test@test.com",
                "password": "testpass123!",
                "password2": "differentpass!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_username_rejected(self, api_client, candidate_user):
        """Duplicate username fails validation."""
        response = api_client.post(
            "/api/v1/accounts/register/candidate/",
            {
                "username": "testcandidate",  # same as fixture
                "email": "different@test.com",
                "password": "testpass123!",
                "password2": "testpass123!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProfileEndpoints:
    def test_candidate_can_view_own_profile(self, candidate_client):
        response = candidate_client.get("/api/v1/accounts/profile/candidate/")
        assert response.status_code == status.HTTP_200_OK

    def test_company_cannot_view_candidate_profile(self, company_client):
        response = company_client.get("/api/v1/accounts/profile/candidate/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_candidate_can_update_profile(self, candidate_client):
        response = candidate_client.patch(
            "/api/v1/accounts/profile/candidate/",
            {"bio": "Backend engineer targeting Japan.", "years_of_experience": 2},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["bio"] == "Backend engineer targeting Japan."

    def test_company_can_view_own_profile(self, company_client):
        response = company_client.get("/api/v1/accounts/profile/company/")
        assert response.status_code == status.HTTP_200_OK

    def test_candidate_cannot_view_company_profile(self, candidate_client):
        response = candidate_client.get("/api/v1/accounts/profile/company/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_company_can_update_profile(self, company_client):
        response = company_client.patch(
            "/api/v1/accounts/profile/company/",
            {"description": "Leading tech company in Tokyo."},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestJWT:
    def test_login_returns_tokens(self, api_client, candidate_user):
        """Login returns access and refresh tokens."""
        response = api_client.post(
            "/api/v1/accounts/token/",
            {
                "username": "testcandidate",
                "password": "testpass123!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_returns_custom_claims(self, api_client, candidate_user):
        """Login response includes role, username, email."""
        response = api_client.post(
            "/api/v1/accounts/token/",
            {
                "username": "testcandidate",
                "password": "testpass123!",
            },
            format="json",
        )
        assert response.data["role"] == "candidate"
        assert response.data["username"] == "testcandidate"
        assert response.data["email"] == "candidate@test.com"

    def test_wrong_password_rejected(self, api_client, candidate_user):
        """Wrong password returns 401."""
        response = api_client.post(
            "/api/v1/accounts/token/",
            {
                "username": "testcandidate",
                "password": "wrongpassword",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_requires_authentication(self, api_client):
        """GET /me/ without token returns 401."""
        response = api_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_returns_user_data(self, candidate_client, candidate_user):
        """GET /me/ returns correct user data."""
        response = candidate_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testcandidate"
        assert response.data["role"] == "candidate"
        # password should never be in response
        assert "password" not in response.data


@pytest.mark.django_db
class TestAuthIntegration:
    """
    Tests the full auth flow end-to-end including DB writes.
    These catch issues like missing migrations that unit tests miss.
    """

    def test_full_login_flow(self, api_client, candidate_user):
        """
        Full login → token stored in DB → refresh → logout.
        Catches: missing token_blacklist tables, migration issues.
        """
        # step 1 — login
        response = api_client.post('/api/v1/accounts/token/', {
            'username': 'testcandidate',
            'password': 'testpass123!',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        access = response.data['access']
        refresh = response.data['refresh']

        # step 2 — use access token on protected endpoint
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        me_response = api_client.get('/api/v1/accounts/me/')
        assert me_response.status_code == status.HTTP_200_OK

        # step 3 — refresh the token
        refresh_response = api_client.post('/api/v1/accounts/token/refresh/', {
            'refresh': refresh,
        }, format='json')
        assert refresh_response.status_code == status.HTTP_200_OK
        new_access = refresh_response.data['access']
        new_refresh = refresh_response.data['refresh']

        # step 4 — logout blacklists the refresh token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access}')
        logout_response = api_client.post('/api/v1/accounts/logout/', {
            'refresh': new_refresh,
        }, format='json')
        assert logout_response.status_code == status.HTTP_205_RESET_CONTENT

        # step 5 — blacklisted token cannot be used again
        blocked = api_client.post('/api/v1/accounts/token/refresh/', {
            'refresh': new_refresh,
        }, format='json')
        assert blocked.status_code == status.HTTP_401_UNAUTHORIZED

    def test_company_can_create_and_delete_job(
        self, api_client, company_user
    ):
        """
        Full company flow — login → create job → soft delete.
        Catches: permission issues, DB write failures.
        """
        # login as company
        response = api_client.post('/api/v1/accounts/token/', {
            'username': 'testcompany',
            'password': 'testpass123!',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        access = response.data['access']

        # create a job
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        create_response = api_client.post('/api/v1/jobs/', {
            'title': 'Integration Test Engineer Tokyo',
            'description': 'Full integration test job listing for CI verification.',
            'job_type': 'full_time',
            'experience_level': 'mid',
            'location': 'Tokyo',
            'is_remote': False,
            'salary_min': 6000000,
            'salary_max': 9000000,
        }, format='json')
        assert create_response.status_code == status.HTTP_201_CREATED
        job_id = create_response.data['id']

        # soft delete it
        delete_response = api_client.delete(f'/api/v1/jobs/{job_id}/')
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    def test_candidate_can_apply(
        self, api_client, candidate_user, job_listing
    ):
        """
        Full candidate flow — login → apply → view application.
        Catches: application DB write failures.
        """
        response = api_client.post('/api/v1/accounts/token/', {
            'username': 'testcandidate',
            'password': 'testpass123!',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        access = response.data['access']

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        apply_response = api_client.post('/api/v1/applications/', {
            'job': job_listing.id,
            'cover_letter': 'Integration test application.',
        }, format='json')
        assert apply_response.status_code == status.HTTP_201_CREATED

        # verify it appears in their list
        list_response = api_client.get('/api/v1/applications/')
        assert list_response.status_code == status.HTTP_200_OK
        assert list_response.data['count'] >= 1

@pytest.mark.django_db
class TestLogout:

    def test_logout_blacklists_refresh_token(self, api_client, candidate_user):
        """Logging out blacklists the refresh token."""
        # login to get tokens
        response = api_client.post('/api/v1/accounts/token/', {
            'username': 'testcandidate',
            'password': 'testpass123!',
        }, format='json')
        refresh_token = response.data['refresh']
        access_token = response.data['access']

        # logout
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = api_client.post('/api/v1/accounts/logout/', {
            'refresh': refresh_token,
        }, format='json')
        assert logout_response.status_code == status.HTTP_205_RESET_CONTENT

    def test_blacklisted_token_cannot_refresh(self, api_client, candidate_user):
        """After logout, refresh token cannot be used to get new access token."""
        # login
        response = api_client.post('/api/v1/accounts/token/', {
            'username': 'testcandidate',
            'password': 'testpass123!',
        }, format='json')
        refresh_token = response.data['refresh']
        access_token = response.data['access']

        # logout — blacklists the refresh token
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        api_client.post('/api/v1/accounts/logout/', {
            'refresh': refresh_token,
        }, format='json')

        # try to use the blacklisted refresh token
        refresh_response = api_client.post('/api/v1/accounts/token/refresh/', {
            'refresh': refresh_token,
        }, format='json')

        # should be rejected
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_requires_authentication(self, api_client):
        """Cannot logout without being authenticated."""
        response = api_client.post('/api/v1/accounts/logout/', {
            'refresh': 'some-token',
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_refresh_token_returns_400(self, candidate_client):
        """Logout without providing refresh token returns 400."""
        response = candidate_client.post('/api/v1/accounts/logout/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
