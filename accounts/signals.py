# accounts/signals.py
import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CandidateProfile, User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def handle_user_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    # auto-create candidate profile
    if instance.role == User.Role.CANDIDATE:
        profile, was_created = CandidateProfile.objects.get_or_create(user=instance)
        if was_created:
            logger.info(f"CandidateProfile created for: {instance.email}")

    # send welcome email via Celery
    from .tasks import send_welcome_email

    transaction.on_commit(lambda: send_welcome_email.delay(instance.id))
