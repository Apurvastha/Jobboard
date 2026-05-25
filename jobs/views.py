from django.views import View
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from . models import JobListing, Category



#business logic

class JobListView(ListView):

    def get_queryset(self):
        #start with active jobs - optimised query
        queryset = JobListing.objects.filter(
            is_active = True
        ).select_related(
            'company', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-posted_at')

        #get query parameters for filtering
        location = self.request.GET.get('location')
        job_type = self.request.GET.get('job_type')
        is_remote = self.request.GET.get('is_remote')
        search = self.request.GET.get('search')


        #apply filters if provided
        if location:
            queryset = queryset.filter(location__icontains=location)
 
        if job_type:
            queryset = queryset.filter(job_type=job_type)

        if is_remote:
            queryset = queryset.filter(is_remote=is_remote.lower() == 'true')

        if search:
            queryset = queryset.filter(
                Q(title__icontains = search) |
                Q(description__icontains = search)
                )
            
        return queryset
            
        #serialize to dict manually- not using drf right now
    def render_to_response(self, context, **kwargs):
        jobs = self.get_queryset()
        data = [
            {
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
            }
            for job in jobs
        ]

        return JsonResponse({'count': len(data), 'jobs': data})

class JobDetailView(DetailView):

    queryset =  JobListing.objects.select_related(
                'company', 'category'
            ).prefetch_related('tags')
   
    def render_to_response(self, context, **kwargs):
       
        job = self.get_object()
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


class JobsByCategoryView(DetailView):

    model = Category
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def render_to_response(self, context, **kwargs):
        category = self.get_object()
        jobs = JobListing.objects.filter(
            category=category,
            is_active=True
        ).select_related('company').order_by('-posted_at')

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