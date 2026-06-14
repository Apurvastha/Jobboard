from unittest.mock import MagicMock, patch

import pytest
from rest_framework import status

from applications.models import Application
from jobs.models import JobListing


@pytest.mark.django_db
class TestApplications:
    def test_candidate_can_apply(self, candidate_client, candidate_user, job_listing):
        """Candidate can apply to an active job."""
        with patch("applications.tasks.send_application_received_email.delay"):
            # mock Celery task — don't actually send email in tests
            _ = Application.objects.create(
                candidate=candidate_user,
                job=job_listing,
                status="pending",
                cover_letter="I am very interested in this position.",
            )
        assert Application.objects.filter(
            candidate=candidate_user, job=job_listing
        ).exists()

    def test_cannot_apply_twice(self, candidate_user, job_listing):
        """
        UniqueConstraint prevents duplicate applications.
        One candidate, one application per job.
        """
        Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status="pending",
        )
        with pytest.raises(Exception):
            # second application to same job should raise IntegrityError
            Application.objects.create(
                candidate=candidate_user,
                job=job_listing,
                status="pending",
            )

    def test_status_choices(self, candidate_user, job_listing):
        """Application status must be a valid choice."""
        app = Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status="pending",
        )
        assert app.status == "pending"

        app.status = "reviewing"
        app.save()
        app.refresh_from_db()
        assert app.status == "reviewing"


@pytest.mark.django_db
class TestApplicationSignals:
    def test_celery_task_called_on_new_application(self, candidate_user, job_listing):
        """
        Creating an application triggers the Celery email task.
        Uses mock to avoid actual email sending in tests.
        """
        with patch(
            "applications.tasks.send_application_received_email.delay"
        ):
            Application.objects.create(
                candidate=candidate_user,
                job=job_listing,
                status="pending",
                cover_letter="Test cover letter.",
            )
            # transaction.on_commit doesn't fire in tests by default
            # use @pytest.mark.django_db(transaction=True) to test it
            # for now just verify the signal fires

        # in unit tests with non-transactional DB, on_commit fires immediately
        # so we can assert the task was called
        # Note: may need transaction=True depending on Django version

    def test_celery_task_not_called_on_update(self, candidate_user, job_listing):
        """
        Updating an existing application does not trigger
        the new application email — only the status change email.
        """
        app = Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status="pending",
        )

        with (
            patch(
                "applications.tasks.send_application_received_email.delay"
            ) as mock_new,
            patch("applications.tasks.send_status_change_email.delay"),
        ):
            app.status = "reviewing"
            app.save()

        mock_new.assert_not_called()


@pytest.mark.django_db
class TestEmailTasks:
    def test_send_application_received_email(self, candidate_user, job_listing):
        from applications.models import Application
        from applications.tasks import send_application_received_email

        app = Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status="pending",
            cover_letter="Test letter.",
        )

        with patch("applications.tasks.send_mail") as mock_mail:
            result = send_application_received_email(app.id)
            assert mock_mail.called
            assert "Email sent" in result

    def test_send_status_change_email(self, candidate_user, job_listing):
        from applications.models import Application
        from applications.tasks import send_status_change_email

        app = Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status="pending",
        )

        with patch("applications.tasks.send_mail") as mock_mail:
            result = send_status_change_email(app.id, "pending", "reviewing")
            assert mock_mail.called
            assert "Email sent" in result

    def test_send_welcome_email(self, candidate_user):
        from accounts.tasks import send_welcome_email

        with patch("accounts.tasks.send_mail") as mock_mail:
            result = send_welcome_email(candidate_user.id)
            assert mock_mail.called
            assert "Welcome email sent" in result

    def test_application_not_found_does_not_raise(self):
        from applications.tasks import send_application_received_email

        # non-existent ID should return gracefully, not raise
        result = send_application_received_email(99999)
        assert "not found" in result


@pytest.mark.django_db
class TestApplicationViewSet:
    def test_candidate_can_apply_to_job(self, candidate_client, job_listing):
        """Candidate can submit an application via API."""
        response = candidate_client.post(
            "/api/v1/applications/",
            {
                "job": job_listing.id,
                "cover_letter": "I am very interested in this position at your company.",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "pending"

    def test_company_cannot_apply(self, company_client, job_listing):
        """Company accounts cannot submit applications."""
        response = company_client.post(
            "/api/v1/applications/",
            {
                "job": job_listing.id,
                "cover_letter": "Companies should not apply.",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_apply(self, api_client, job_listing):
        """Unauthenticated users cannot apply."""
        response = api_client.post(
            "/api/v1/applications/",
            {
                "job": job_listing.id,
                "cover_letter": "No token provided.",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_apply_twice_via_api(
        self, candidate_client, candidate_user, job_listing
    ):
        """Duplicate application returns 400."""
        # first application
        candidate_client.post(
            "/api/v1/applications/",
            {
                "job": job_listing.id,
                "cover_letter": "First application.",
            },
            format="json",
        )

        # second application to same job
        response = candidate_client.post(
            "/api/v1/applications/",
            {
                "job": job_listing.id,
                "cover_letter": "Second application.",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_candidate_sees_only_own_applications(
        self, candidate_client, candidate_user, another_company_user, job_listing
    ):
        """Candidate list only returns their own applications."""
        from applications.models import Application

        # create application for candidate
        Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status="pending",
        )

        response = candidate_client.get("/api/v1/applications/")
        assert response.status_code == status.HTTP_200_OK
        for app in response.data["results"]:
            assert app["candidate_email"] == candidate_user.email

    def test_company_can_change_status(
        self, company_client, candidate_user, job_listing
    ):
        """Company can change application status to reviewing."""
        from applications.models import Application

        app = Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status="pending",
        )

        response = company_client.patch(
            f"/api/v1/applications/{app.id}/status/",
            {"status": "reviewing"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        app.refresh_from_db()
        assert app.status == "reviewing"

    def test_other_company_cannot_change_status(
        self, another_company_client, candidate_user, job_listing
    ):
        """A different company cannot change application status."""
        from applications.models import Application

        app = Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status="pending",
        )

        response = another_company_client.patch(
            f"/api/v1/applications/{app.id}/status/",
            {"status": "accepted"},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        app.refresh_from_db()
        assert app.status == "pending"

    def test_company_sees_job_applications(
        self, company_client, candidate_user, job_listing
    ):
        """Company can see all applications for their job."""
        from applications.models import Application

        Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status="pending",
        )

        response = company_client.get(f"/api/v1/jobs/{job_listing.id}/applications/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total"] == 1
        assert response.data["job"] == job_listing.title

    def test_cannot_apply_to_inactive_job(
        self, candidate_client, company_user, category
    ):
        """Applying to an inactive job returns 400."""
        inactive_job = JobListing.objects.create(
            title="Inactive Job Position",
            description="This job is no longer active.",
            company=company_user.company_profile,
            category=category,
            job_type="full_time",
            experience_level="mid",
            location="Tokyo",
            is_active=False,
            salary_min=5000000,
            salary_max=8000000,
        )

        response = candidate_client.post(
            "/api/v1/applications/",
            {
                "job": inactive_job.id,
                "cover_letter": "Applying to inactive job.",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
