from django.db.models.signals import post_save
from django.dispatch import receiver
from . models import User, CandidateProfile, CompanyProfile

@receiver(post_save, sender=User)
def create_profile_on_registration(sender, instance, created, **kwargs):
    if not created:
        return
    
    if instance.role == User.Role.CANDIDATE:
        CandidateProfile.objects.get_or_create(user=instance)
        