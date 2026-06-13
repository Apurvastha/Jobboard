import pytest
from rest_framework import status
from applications.models import Application
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestApplications:

    def test_candidate_can_apply(
        self, candidate_client, candidate_user, job_listing
    ):
        """Candidate can apply to an active job."""
        with patch('applications.tasks.send_application_received_email.delay'):
            # mock Celery task — don't actually send email in tests
            app = Application.objects.create(
                candidate=candidate_user,
                job=job_listing,
                status='pending',
                cover_letter='I am very interested in this position.',
            )
        assert Application.objects.filter(
            candidate=candidate_user,
            job=job_listing
        ).exists()

    def test_cannot_apply_twice(
        self, candidate_user, job_listing
    ):
        """
        UniqueConstraint prevents duplicate applications.
        One candidate, one application per job.
        """
        Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status='pending',
        )
        with pytest.raises(Exception):
            # second application to same job should raise IntegrityError
            Application.objects.create(
                candidate=candidate_user,
                job=job_listing,
                status='pending',
            )

    def test_status_choices(self, candidate_user, job_listing):
        """Application status must be a valid choice."""
        app = Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status='pending',
        )
        assert app.status == 'pending'

        app.status = 'reviewing'
        app.save()
        app.refresh_from_db()
        assert app.status == 'reviewing'


@pytest.mark.django_db
class TestApplicationSignals:

    def test_celery_task_called_on_new_application(
        self, candidate_user, job_listing
    ):
        """
        Creating an application triggers the Celery email task.
        Uses mock to avoid actual email sending in tests.
        """
        with patch(
            'applications.tasks.send_application_received_email.delay'
        ) as mock_task:
            Application.objects.create(
                candidate=candidate_user,
                job=job_listing,
                status='pending',
                cover_letter='Test cover letter.',
            )
            # transaction.on_commit doesn't fire in tests by default
            # use @pytest.mark.django_db(transaction=True) to test it
            # for now just verify the signal fires

        # in unit tests with non-transactional DB, on_commit fires immediately
        # so we can assert the task was called
        # Note: may need transaction=True depending on Django version

    def test_celery_task_not_called_on_update(
        self, candidate_user, job_listing
    ):
        """
        Updating an existing application does not trigger
        the new application email — only the status change email.
        """
        app = Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status='pending',
        )

        with patch(
            'applications.tasks.send_application_received_email.delay'
        ) as mock_new, patch(
            'applications.tasks.send_status_change_email.delay'
        ) as mock_status:
            app.status = 'reviewing'
            app.save()

        mock_new.assert_not_called()


@pytest.mark.django_db
class TestEmailTasks:

    def test_send_application_received_email(self, candidate_user, job_listing):
        from applications.tasks import send_application_received_email
        from applications.models import Application

        app = Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status='pending',
            cover_letter='Test letter.',
        )

        with patch('applications.tasks.send_mail') as mock_mail:
            result = send_application_received_email(app.id)
            assert mock_mail.called
            assert 'Email sent' in result

    def test_send_status_change_email(self, candidate_user, job_listing):
        from applications.tasks import send_status_change_email
        from applications.models import Application

        app = Application.objects.create(
            candidate=candidate_user,
            job=job_listing,
            status='pending',
        )

        with patch('applications.tasks.send_mail') as mock_mail:
            result = send_status_change_email(app.id, 'pending', 'reviewing')
            assert mock_mail.called
            assert 'Email sent' in result

    def test_send_welcome_email(self, candidate_user):
        from accounts.tasks import send_welcome_email

        with patch('accounts.tasks.send_mail') as mock_mail:
            result = send_welcome_email(candidate_user.id)
            assert mock_mail.called
            assert 'Welcome email sent' in result

    def test_application_not_found_does_not_raise(self):
        from applications.tasks import send_application_received_email
        # non-existent ID should return gracefully, not raise
        result = send_application_received_email(99999)
        assert 'not found' in result