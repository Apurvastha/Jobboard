from django.core.cache import cache
import logging
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver, Signal
from .models import JobListing, Category



logger = logging.getLogger(__name__)


@receiver(post_save, sender=JobListing)
def log_job_listing_changes(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f'New job listing: "{instance.title}" '
            f'by {instance.company.name}'
        )
    else:
        logger.info(
            f'Job listing updated: "{instance.title}" '
            f'is_active={instance.is_active}'
        )


@receiver(pre_delete, sender=JobListing)
def log_job_listing_deletion(sender, instance, **kwargs):
    # pre_delete fires before deletion
    # at this point the object still exists in the DB
    # post_delete fires after - object is gone
    logger.info(
        f'Job lsiting being deleted: "{instance.title}" '
        f'company={instance.company.name}'
        f'application_count={instance.applications.count()}' 
    )

@receiver([post_save,post_delete], sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    cache.delete('all_categories')

@receiver(post_save, sender=JobListing)
def invalidate_job_cache(sender, instance, **kwargs):
    cache.delete(f'job:{instance.pk}')
    cache.delete('featured_jobs')
    logger.info(f'Job cache invalidated: job:{instance.pk}')


    
