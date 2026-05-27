from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        CANDIDATE = 'candidate', 'Candidate'
        COMPANY = 'company', 'Company'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CANDIDATE
    )

    def __str__(self):
        return self.email
    
    #helper properties - clean role checks anywhere in the codebase
    @property
    def is_candidate(self):
        return self.role == self.Role.CANDIDATE
    
    @property
    def is_company(self):
        return self.role == self.Role.COMPANY

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    # check if user has completed their profile

    @property
    def has_company_profile(self):
        return hasattr(self, 'company_profile')
    
    @property
    def has_candidate_profile(self):
        return hasattr(self, 'candidate_profile')
class CompanyProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='company_profile'
    )
    name = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=100, default='Japan')
    founded_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class CandidateProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='candidate_profile'
    )
    bio = models.TextField(blank=True)
    resume_url = models.URLField(blank=True)
    years_of_experience = models.IntegerField(default=0)
    skills = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.email} - candidate'