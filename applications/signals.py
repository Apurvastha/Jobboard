import logging

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="applications.Application")
def handle_application_post_save(sender, instance, created, **kwargs):
    from applications.tasks import (
        send_application_received_email,
        send_status_change_email,
        send_notification_to_service
    )

    if created:
        # new application - notify the company
        logger.info(
            f"New Application signal: {instance.candidate.email}-> {instance.job.title}"
        )
        # transaction.on_commit ensures tasks fires after DB commit
        transaction.on_commit(
            lambda: send_application_received_email.delay(instance.id)
        )
        

    else:
        # status update — notify the candidate
        # we need to know the old status to include in the email
        # Django doesn't give us the old value directly in post_save
        # so we track it via a pre_save signal below
        if hasattr(instance, "_old_status") and instance._old_status != instance.status:
            old_status = instance._old_status
            new_status = instance.status

            logger.info(
                f"Status change signal: {instance.candidate.email} "
                f"| {old_status} → {new_status}"
            )

            transaction.on_commit(
                lambda: send_status_change_email.delay(
                    instance.id,
                    old_status,
                    new_status,
                )
            )
            transaction.on_commit(
                lambda: send_notification_to_service.delay(
                    instance.id,
                    old_status,
                    new_status,
                )
            )



@receiver(pre_save, sender="applications.Application")
def capture_old_status(sender, instance, **kwargs):
    """
    Captures the old status before save so post_save can compare.
    Only runs for existing objects (not new ones).
    """
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None
