from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Q
from . models import JobListing, Category
from .forms import JobSearchForm



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

        #validate query params through the form
        form = JobSearchForm(self.request.GET)
        if not form.is_valid():
            return queryset
        
        cd = form.cleaned_data


        #apply filters if provided
        if cd.get('search'):
            queryset = queryset.filter(
                Q(title__icontains=cd['search']) |
                Q(description__icontains=cd['search'])
            )
        if cd.get('location'):
            queryset = queryset.filter(location__icontains=cd['location'])
        if cd.get('job_type'):
            queryset = queryset.filter(job_type=cd['job_type'])
        if cd.get('experience_level'):
            queryset = queryset.filter(experience_level=cd['experience_level'])
        if cd.get('salary_min'):
            queryset = queryset.filter(salary_min__gte=cd['salary_min'])
        if cd.get('salary_max'):
            queryset = queryset.filter(salary_max__lte=cd['salary_max'])
        if cd.get('is_remote'):
            queryset = queryset.filter(is_remote=cd['is_remote'])
        if cd.get('category'):
            queryset = queryset.filter(category=cd['category'])
            
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
    

# add to jobs/views.py temporarily
def broken_view(request):
    raise ValueError("something went wrong")