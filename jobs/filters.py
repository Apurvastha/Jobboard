import django_filters
from .models import JobListing, Category


class JobListingFilter(django_filters.FilterSet):
    
    # exact match filters
    job_type = django_filters.ChoiceFilter(
        choices = JobListing.JobType.choices
    )
    experience_level = django_filters.ChoiceFilter(
        choices=JobListing.ExperienceLevel.choices
    )
    is_remote = django_filters.BooleanFilter()
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category'
    )

    # slug lookup fro category - more API friendly
    # /jobs/?category_slug=backend instead of /jobs/?category=1
    category_slug = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )

    #partial match filters
    location = django_filters.CharFilter(
        lookup_expr='icontains'
    )

    # range filters for salary
    salary_min = django_filters.NumberFilter(
        field_name='salary_min',
        lookup_expr='gte' # salary_min >= value
    )

    salary_max = django_filters.NumberFilter(
        field_name='salary_max',
        lookup_expr='lte' # salary_max <= value
    )

    # combined salary range
    # /jobs/?min_salary=50000000&max_salary=10000000000
    min_salary = django_filters.NumberFilter(
        field_name='salary_min',
        lookup_expr='gte'
    )
    max_salary = django_filters.NumberFilter(
        field_name='salary_max',
        lookup_expr='lte'
    )

    # date range filters
    posted_after = django_filters.DateFilter(
        field_name='posted_at',
        lookup_expr='date__gte'
    )
    posted_before = django_filters.DateFilter(
        field_name='posted_at',
        lookup_expr='date__lte'
    )

    class Meta:
        model = JobListing
        fields = [
            'job_type',
            'experience_level',
            'is_remote',
            'location',
            'category',
            'category_slug',
            'salary_min',
            'salary_max',
            'min_salary',
            'max_salary',
            'posted_after',
            'posted_before',
        ]
    