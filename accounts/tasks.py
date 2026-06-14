import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id):
    """
    Sends welcome email to new users after registration.
    """
    try:
        from accounts.models import User

        user = User.objects.get(id=user_id)

        role_message = {
            "candidate": "Start exploring job opportunities and apply to positions that match your skills.",
            "company": "Start posting job listings and find the best candidates for your team.",
        }.get(user.role, "Welcome to JobBoard")

        send_mail(
            subject="Welcome to JobBoard",
            message=f"""
Hi {user.username},

Welcome to JobBoard! Your account has been created successfully.

{role_message}

Best regards,
JobBoard Team
            """.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to {user.email}")
        return f"Welcome email sent to {user.email}"

    except Exception as exc:
        logger.error(f"Failed to send welcome email: {exc}")
        raise self.retry(exc=exc, countdown=60)
