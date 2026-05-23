from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from . models import JobListing, Category



#business logic


@require_http_methods(['GET'])
def job_list(request):
    #get query parameters for filtering
    location = request.GET.get('location')
    job_type = request.GET.get('job_type')
    is_remote = request.GET.get('is_remote')
    search = request.GET.get('search')

    #start with active jobs - optimised query
    jobs = JobListing.objects.filter(
        is_active = True
    ).select_related(
        'company', 'category'
    ).prefetch_related(
        'tags'
    ).order_by('-posted_at')

    #apply filters if provided
    if location:
        jobs =jobs.filter(location__icontains=location)

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    if is_remote:
        jobs = jobs.filter(is_remote=is_remote.lower() == 'true')

    if search:
        from django.db.models import Q
        jobs = jobs.filter(\
            Q(title__icontains = search) |
            Q(descriptions__icontains = search)
            )
        
    #serialize to dict manually- not using drf right now
    data = []
    for job in jobs:
        data.append({
            'id': job.id,
            'title': job.title,
            'company': job.company.name,
            'category': job.category.name if job.category else None,
            'job_type': job.job_type,
            'experience_level': job.experience_level,
            'location': job.location,
            'is_remote': job.is_remote,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'tags': [tag.name for tag in job.tags.all()],
            'posted_at': job.posted_at,
        })

    return JsonResponse({'count': len(data), 'jobs': data})


@require_http_methods(['GET'])
def job_detail(request, pk):
    job = get_object_or_404(
        JobListing.objects.select_related(
            'company', 'category'
        ).prefetch_related(
            'tags'
        ), 
        pk=pk,
        is_active = True
    )

    data = {
        'id': job.id,
        'title': job.title,
        'description': job.description,
        'company': {
            'id': job.company.id,
            'name': job.company.name,
            'website': job.company.website,
            'country': job.company.country,
            },
        'category': job.category.name if job.category else None,
        'job_type': job.job_type,
        'experience_level': job.experience_level,
        'location': job.location,
        'is_remote': job.is_remote,
        'salary_min': job.salary_min,
        'salary_max': job.salary_max,
        'tags': [tag.name for tag in job.tags.all()],
        'deadline': job.deadline.isoformat() if job.deadline else None,
        'posted_at': job.posted_at.isoformat(),
    }

    return JsonResponse(data)

@require_http_methods(['GET'])
def jobs_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)

    jobs = JobListing.objects.filter(
        category=category,
        is_active = True
    ).select_related(
        'company', 'category'
    ).prefetch_related(
        'tags'
    ).order_by('-posted_at')

    data = {
        'category': category.name,
        'count': jobs.count(),
        'jobs': [
            {
                'id': job.id,
                'title': job.title,
                'company': job.company.name,
                'location': job.location,
                'is_remote': job.is_remote,
                'posted_at': job.posted_at.isoformat(),
            }
            for job in jobs
        ]
    }

    return JsonResponse(data)