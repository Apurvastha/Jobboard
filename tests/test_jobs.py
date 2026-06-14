import pytest
from django.urls import reverse
from rest_framework import status

from jobs.models import JobListing


@pytest.mark.django_db
class TestJobListingList:
    def test_anyone_can_list_jobs(self, api_client, multiple_job_listings):
        """GET /jobs/ is public - no auth required."""
        response = api_client.get("/api/v1/jobs/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 5

    def test_list_is_paginated(self, api_client, multiple_job_listings):
        """Response includes pagination metadata."""
        response = api_client.get("/api/v1/jobs/")
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data
        assert "total_pages" in response.data
        assert "current_page" in response.data

    def test_filter_by_location(self, api_client, multiple_job_listings):
        """?location=Tokyo only returns Tokyo jobs."""
        response = api_client.get("/api/v1/jobs/?location=Tokyo")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        for job in response.data["results"]:
            assert "Tokyo" in job["location"]

    def test_filter_by_remote(self, api_client, multiple_job_listings):
        """?is_remote=true returns only remote jobs"""
        response = api_client.get("/api/v1/jobs/?is_remote=true")
        assert response.status_code == status.HTTP_200_OK
        for job in response.data["results"]:
            assert job["is_remote"] is True

    def test_search_by_title(self, api_client, multiple_job_listings):
        """?search=Engineer returns matching jobs."""
        response = api_client.get("/api/v1/jobs/?search=Engineer")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] > 0

    def test_ordering_by_salary(self, api_client, multiple_job_listings):
        """?ordering=-salary_max returns highest paying first."""
        response = api_client.get("/api/v1/jobs/?ordering=-salary_max")
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        if len(results) > 1:
            assert results[0]["salary_max"] >= results[1]["salary_max"]

    def test_inactive_jobs_not_in_list(self, api_client, company_user, category):
        """Inactive jobs are hidden from the listing."""
        JobListing.objects.create(
            title="Inactive Job",
            description="This should not appear.",
            company=company_user.company_profile,
            category=category,
            job_type="full_time",
            experience_level="mid",
            location="Tokyo",
            is_active=False,  # inactive
            salary_min=5000000,
            salary_max=8000000,
        )
        response = api_client.get("/api/v1/jobs/")
        titles = [j["title"] for j in response.data["results"]]
        assert "Inactive Job" not in titles

    def test_no_n_plus_1_on_list(
        self, api_client, multiple_job_listings, django_assert_num_queries
    ):
        """
        Query count stays constant regardless of job count.
        This test FAILS if N+1 is introduced.
        """
        with django_assert_num_queries(3):
            # 1: count query for pagination
            # 2: jobs + companies + categories (select_related JOIN)
            # 3: tags (prefetch_related)
            response = api_client.get("/api/v1/jobs/")
            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestJobListingCreate:
    def test_company_can_create_job(self, company_client, category):
        """Company users can create job listings."""
        response = company_client.post(
            "/api/v1/jobs/",
            {
                "title": "New Python Engineer Tokyo",
                "description": "We need an experienced Python Engineer.",
                "job_type": "full_time",
                "experience_level": "senior",
                "location": "Tokyo",
                "is_remote": False,
                "salary_min": 7000000,
                "salary_max": 10000000,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Python Engineer Tokyo"
        assert JobListing.objects.filter(title="New Python Engineer Tokyo").exists()

    def test_candidate_cannot_create_job(self, candidate_client, category):
        """Candidates are forbidden from creating job listings."""
        response = candidate_client.post(
            "/api/v1/jobs/",
            {
                "title": "Unauthorized Job Post",
                "description": "This should not be created.",
                "job_type": "full_time",
                "experience_level": "mid",
                "location": "Tokyo",
                "is_remote": False,
                "salary_min": 5000000,
                "salary_max": 8000000,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not JobListing.objects.filter(title="Unauthorized Job Post").exists()

    def test_unauthenticated_cannot_create_job(self, api_client):
        """Unauthenticated requests cannot create job listings."""
        response = api_client.post(
            "/api/v1/jobs/",
            {
                "title": "Hacker Job",
                "description": "Should fail.",
                "job_type": "full_time",
                "experience_level": "mid",
                "location": "Tokyo",
                "is_remote": False,
                "salary_min": 5000000,
                "salary_max": 8000000,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_job_auto_assigned_to_logged_in_company(self, company_client, company_user):
        """company_id is set from request.user, not from client input."""
        response = company_client.post(
            "/api/v1/jobs/",
            {
                "title": "Auto Assigned Company Test",
                "description": "Company should be set automatically.",
                "job_type": "full_time",
                "experience_level": "mid",
                "location": "Tokyo",
                "is_remote": False,
                "salary_min": 5000000,
                "salary_max": 8000000,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        job = JobListing.objects.get(title="Auto Assigned Company Test")
        assert job.company == company_user.company_profile

    def test_title_too_short_rejected(self, company_client):
        """Title under 10 characters fails validation."""
        response = company_client.post(
            "/api/v1/jobs/",
            {
                "title": "Short",  # less than 10 chars
                "description": "Valid description here.",
                "job_type": "full_time",
                "experience_level": "mid",
                "location": "Tokyo",
                "is_remote": False,
                "salary_min": 5000000,
                "salary_max": 8000000,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.data


@pytest.mark.django_db
class TestJobListingUpdate:
    def test_owner_can_update_job(self, company_client, job_listing):
        """Company that owns the job can update it."""
        response = company_client.patch(
            f"/api/v1/jobs/{job_listing.id}/", {"salary_min": 9000000}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        job_listing.refresh_from_db()
        assert job_listing.salary_min == 9000000

    def test_other_company_cannot_update_job(self, another_company_client, job_listing):
        """A different company cannot edit someone else's job."""
        response = another_company_client.patch(
            f"/api/v1/jobs/{job_listing.id}/",
            {"title": "Stolen Title XXXXXXXXXX"},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        job_listing.refresh_from_db()
        assert job_listing.title != "Stolen Title XXXXXXXXXX"

    def test_candidate_cannot_update_job(self, candidate_client, job_listing):
        """Candidates cannot update any job listing."""
        response = candidate_client.patch(
            f"/api/v1/jobs/{job_listing.id}/", {"salary_min": 1000000}, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestJobListingDelete:
    def test_delete_is_soft(self, company_client, job_listing):
        """DELETE sets is_active=False instead of removing the row."""
        response = company_client.delete(f"/api/v1/jobs/{job_listing.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # row still exists in DB
        job_listing.refresh_from_db()
        assert job_listing.is_active is False

    def test_other_company_cannot_delete(self, another_company_client, job_listing):
        """A different company cannot soft-delete someone else's job."""
        response = another_company_client.delete(f"/api/v1/jobs/{job_listing.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        job_listing.refresh_from_db()
        assert job_listing.is_active is True


@pytest.mark.django_db
class TestFeaturedJobs:
    def test_featured_returns_top_5(self, api_client, multiple_job_listings):
        """Featured endpoint returns at most 5 jobs."""
        response = api_client.get("/api/v1/jobs/featured/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) <= 5

    def test_featured_ordered_by_salary(self, api_client, multiple_job_listings):
        """Featured jobs are ordered by salary_max descending."""
        response = api_client.get("/api/v1/jobs/featured/")
        results = response.data
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]["salary_max"] >= results[i + 1]["salary_max"]


@pytest.mark.django_db
class TestJobTasks:
    def test_deactivate_expired_jobs(self, company_user, category):
        from django.utils import timezone

        from jobs.tasks import deactivate_expired_jobs

        # create a job with a past deadline
        expired = JobListing.objects.create(
            title="Expired Position Test",
            description="Should be deactivated.",
            company=company_user.company_profile,
            category=category,
            job_type="full_time",
            experience_level="mid",
            location="Tokyo",
            is_active=True,
            salary_min=5000000,
            salary_max=8000000,
            deadline=timezone.now().date() - timezone.timedelta(days=1),
        )

        result = deactivate_expired_jobs()
        assert "Deactivated" in result

        expired.refresh_from_db()
        assert expired.is_active is False

    def test_deactivate_no_expired_jobs(self):
        from jobs.tasks import deactivate_expired_jobs

        result = deactivate_expired_jobs()
        assert "No expired jobs" in result
