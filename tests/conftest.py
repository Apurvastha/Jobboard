import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from accounts.models import CompanyProfile, CandidateProfile
from jobs.models import JobListing, Category, Tag


User = get_user_model()

@pytest.fixture
def api_client():
    '''Plain API client - no authentication.'''
    return APIClient()

@pytest.fixture
def company_user(db):
    """A user with company role and a company profile."""
    user = User.objects.create_user(
        username='testcompany',
        email='company@test.com',
        password='testpass123!',
        role=User.Role.COMPANY
    )
    CompanyProfile.objects.create(
        user=user,
        name="Test Company",
        country='Japan'
    )
    return user

@pytest.fixture
def candidate_user(db):
    '''A user with candidate role and a candidate profile'''
    user = User.objects.create_user(
        username='testcandidate',
        email='candidate@test.com',
        password='testpass123!',
        role=User.Role.CANDIDATE
    )
    CandidateProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def another_company_user(db):
    '''A second company user - for testing ownership'''
    user = User.objects.create_user(
        username='othercompany',
        email='other@test.com',
        password='testpass123!',
        role=User.Role.COMPANY
    )
    CompanyProfile.objects.create(
        user=user,
        name = 'Other Company',
        country = 'Japan'
    )
    return user

@pytest.fixture
def company_client(company_user):
    '''API client authenticated as company user.'''
    client = APIClient()
    client.force_authenticate(user=company_user)
    return client


@pytest.fixture
def candidate_client(candidate_user):
    '''API client authenticated as candidate user.'''
    client = APIClient()
    client.force_authenticate(user=candidate_user)
    return client

@pytest.fixture
def another_company_client(another_company_user):
    """API client authenticated as a different company."""
    client = APIClient()
    client.force_authenticate(user=another_company_user)
    return client


@pytest.fixture
def category(db):
    return Category.objects.create(name='Backend', slug='backend')


@pytest.fixture
def tag(db):
    return Tag.objects.create(name='Python')

@pytest.fixture
def job_listing(db, company_user, category):
    """A single active job listing owned by company_user."""
    return JobListing.objects.create(
        title='Senior Python Engineer',
        description='We need a senior Python engineer with Django experience.',
        company=company_user.company_profile,
        category=category,
        job_type='full_time',
        experience_level='senior',
        location='Tokyo',
        is_remote=False,
        salary_min=7000000,
        salary_max=10000000,
        is_active=True,
    )


@pytest.fixture
def multiple_job_listings(db, company_user, category):
    """Five job listings for pagination and filter tests."""
    jobs = []
    locations = ['Tokyo', 'Tokyo', 'Osaka', 'Fukuoka', 'Tokyo']
    for i, location in enumerate(locations):
        job = JobListing.objects.create(
            title = f'Engineer Position {i}',
            description=f'Description for position {i}',
            company=company_user.company_profile,
            category=category,
            job_type='full_time',
            experience_level='mid',
            location=location,
            is_remote=(i % 2 == 0),
            salary_min=5000000 + (i * 500000),
            salary_max=8000000 + (i * 500000),
            is_active=True,
        )
        jobs.append(job)
    return jobs