import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Application


logger =logging.getLogger(__name__)


@receiver(post_save, sender=Application)
def notify_on_application_created(sender, instance, created, **kwargs):
    # only fire if new application is created
    if not created:
        return
    
    logger.info(
        f'New Application: {instance.candidate.email}' 
        f' applied to {instance.job.title}'
        f' at {instance.job.company.name}'
        )
    

@receiver(post_save, sender=Application)
def notify_on_status_change(sender, instance, created, **kwargs):

    # only fire when status is updated - not on creation
    if created:
        return
    
    logger.info(
        f'Application status changed: '
        f'{instance.candidate.email} | '
        f'{instance.job.title} | '
        f'new status: {instance.status}'
    )