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
            f'for job: {job_title}'
        )
        return f'Email send to {company_email}'
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

Your application fro {job_title} at {company_name} {status_messages}.

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
            f'Status change email send to {candidate_email}'
            f'({old_status} -> {new_status}) for: {job_title}'
        )
        return f'Email send to {candidate_email}'
    
    except Application.DoesNotExist:
        logger.warning(f'Application {application_id} not found - skipping')
        return f'Application {application_id} not found'
    
    except Exception as exc:
        logger.error(f'Failed to send status change email: {exc}')
        raise self.retry(exc=exc, countdown=60)
    
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id):
    """
    Sends welcome email to new users after registration.
    """
    try:
        from accounts.models import User

        user = User.objects.get(id=user_id)

        role_message = {
            'candidate': 'Start exploring job opportunities and apply to positions that match your skills.',
            'company': 'Start posting job listings and find the best candidates for your team.',
        }.get(user.role, 'Welcome to JobBoard')

        send_mail(
            subject='Welcome to JobBoard',
            message=f'''
Hi {user.username},

Welcome to JobBoard! Your account has been created successfully.

{role_message}

Best regards,
JobBoard Team
            '''.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f'Welcome email sent to {user.email}')
        return f'Welcome email sent to {user.email}'

    except Exception as exc:
        logger.error(f'Failed to send welcome email: {exc}')
        raise self.retry(exc=exc, countdown=60)
        
    


