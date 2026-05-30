import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from . models import User, CandidateProfile, CompanyProfile


logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_profile_on_registration(sender, instance, created, **kwargs):
    # only run when a new user is created
    if not created:
        return
    
    # only create profiles for candidates
    if instance.role != User.Role.CANDIDATE:
        return
    
    profile, was_created = CandidateProfile.objects.get_or_create(
        user= instance
    )

    if was_created:
        logger.info(f'CandidateProfile created for user: {instance.email}')
        