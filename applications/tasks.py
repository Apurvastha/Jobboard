import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_application_received_email(self, application_id):
    """
    Sends email to the company when a new application is received.
    Triggered by post_save signal on Application model.
    """
    try:
        # import here to avoid circular imports
        from .models import Application

        application = Application.objects.select_related(
            'candidate',
            'job',
            'job__company',
            'job__company__user',
        ).get(id=application_id)

        company_email = application.job.company.user.email
        candidate_email = application.candidate.email
        job_title = application.job.title
        company_name = application.job.company.name

        send_mail(
            subject=f'New Application - {job_title}',
            message=f'''
Hi {company_name} team,

You have received a new application for the position: {job_title}

Applicant: {candidate_email}
Status: Pending review

Log in to your dashboard to review the application.

Best regards,
JobBoard Team
            '''.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[company_email],
            fail_silently=False,
        )
        logger.info(
            f'Application received email send to {company_email}'
            f' for job: {job_title}'
        )
        return f'Email sent to {company_email}'
    except Application.DoesNotExist:
        # application was deleted before task ran - dont retry
        logger.warning(f'Application {application_id} not found - skipping email')
        return f'Application {application_id} not found'
    
    except Exception as exc:
        logger.error(f'Failed to send email: {exc}')
        # retry after 60 seconds, upto 3 times
        raise self.retry(exc=exc, countdown=60)
    

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_status_change_email(self, application_id, old_status, new_status):
    """
    Sends email to the candiate when their application status changes.
    Triggered by post_save signal on Application model(updates only)
    """
    try:
        from .models import Application

        application = Application.objects.select_related(
            'candidate',
            'job',
            'job__company',
        ).get(id=application_id)

        candidate_email = application.candidate.email
        job_title = application.job.title
        company_name = application.job.company.name

        status_messages = {
            'pending': 'is pending review',
            'reviewing': 'is currently being reviewed',
            'accepted': 'has been accepted — congratulations!',
            'rejected': 'was not selected this time',
        }

        status_messages = status_messages.get(
            new_status,
            f'has been updated to {new_status}'
        )
        
        send_mail(
            subject=f'Application Update - {job_title} at {company_name}',
            message=f'''
Hi,

Your application for {job_title} at {company_name} {status_messages}.

Previous status: {old_status}
Current_status = {new_status}

{"We will be in touch with next steps soon." if new_status== "accepted" else "Thank you for your interest in this position."}

Best regards,
JobBoard Team
            '''.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate_email],
            fail_silently=False,
        )

        logger.info(
            f'Status change email sent to {candidate_email}'
            f' ({old_status} -> {new_status}) for: {job_title}'
        )
        return f'Email sent to {candidate_email}'
    
    except Application.DoesNotExist:
        logger.warning(f'Application {application_id} not found - skipping')
        return f'Application {application_id} not found'
    
    except Exception as exc:
        logger.error(f'Failed to send status change email: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def remind_unreviewed_applications(self):
    """
    Runs every weekday at 8am.
    Finds companies with pending applications older than 3 days
    and sends them a reminder email.
    """
    try:
        from .models import Application
        from accounts.models import CompanyProfile
        from django.core.mail import send_mail
        from django.conf import settings
        from django.utils import timezone

        three_day_ago = timezone.now() - timezone.timedelta(days=3)

        # find companies that have pending applications older than 3 days
        companies_with_pending = CompanyProfile.objects.filter(
            job_listings__applications__status = 'pending',
            job_listings__applications__applied_at__lt = three_day_ago,
        ).distinct()

        reminded_count = 0

        for company in companies_with_pending.select_related('user'):
            # count how many pending apps this company has
            pending_count = Application.objects.filter(
                job__company=company,
                status='pending',
                applied_at__lt=three_day_ago
            ).count()

            if pending_count == 0:
                continue

            try:
                send_mail(
                    subject=f'Reminder — {pending_count} unreviewed applications',
                    message=f'''
Hi {company.name} team,

You have {pending_count} application(s) waiting for review that were submitted more than 3 days ago.

Please log in to your dashboard to review them.

Best regards,
JobBoard Team
                    '''.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[company.user.email],
                    fail_silently=True,
                )
                reminded_count += 1
                logger.info(
                    f'Reminder sent to {company.name} '
                    f'({pending_count} pending applications)'
                )
            except Exception as e:
                logger.warning(f'Failed to remind {company.name}: {e}')

        return f'Reminders sent to {reminded_count} companies.'

    except Exception as exc:
        logger.error(f'Reminder task failed: {exc}')
        raise self.retry(exc=exc, countdown=300)
    

        
    


