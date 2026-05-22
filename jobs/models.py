from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class JobListing(models.Model):

    class JobType(models.TextChoices):
        FULL_TIME = 'full_time', 'Full Time'
        PART_TIME = 'part_time', 'Part Time'
        CONTRACT = 'contract', 'Contract'
        INTERNSHIP = 'internship', 'Internship'

    class ExperienceLevel(models.TextChoices):
        JUNIOR = 'junior', 'Junior'
        MID = 'mid', 'Mid'
        SENIOR = 'senior', 'Senior'

    #core fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    company = models.ForeignKey(
        'accounts.CompanyProfile',
        on_delete=models.PROTECT,
        related_name='job_listings'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='job_listings'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='job_listings')

    #job details
    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
        default=JobType.FULL_TIME
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.MID
    )
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)

    #status
    is_active = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True)

    #timestamps
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['posted_at']
        indexes = [
            models.Index(fields=['is_active', 'posted_at']), 
            models.Index(fields=['location']),
            models.Index(fields=['job_type'])
        ]
    def __str__(self):
        return f'{self.title} - {self.company}'