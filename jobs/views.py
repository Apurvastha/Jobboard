from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import   AllowAny, IsAuthenticated
from accounts.permissions import  IsOwnerOrReadOnly, IsCompany
from django.db.models import Q
from .models import JobListing, Category
from .serializers import (
    JobListingListSerializer, 
    JobListingSerializer, 
    CategorySerializer,
)

class JobListingViewSet(viewsets.ModelViewSet):
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'featured', 'similar']:
            # read actions - anyone
            return [AllowAny()]
        
        if self.action == 'create':
            # creating - must be a company
            return [IsCompany()]
        
        if self.action in ['update', 'partial_update', 'destroy']:
            # modifying - must be the owner
            return [IsOwnerOrReadOnly()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = JobListing.objects.filter(
            is_active = True
        ).select_related(
            'company', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-posted_at')

        location = self.request.query_params.get('location')
        job_type = self.request.query_params.get('job_type')
        experience_level = self.request.query_params.get('experience_level')
        is_remote = self.request.query_params.get('is_remote')
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')

        if location:
            queryset = queryset.filter(location__icontains=location)
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        if is_remote:
            queryset = queryset.filter(is_remote=is_remote.lower() == 'true')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        if category:
            queryset = queryset.filter(category__slug=category)
        
        return queryset
    
    def get_serializer_class(self):
        # list action uses lightweight serializer
        if self.action == 'list':
            return JobListingListSerializer
        # everything else uses full serializer
        return JobListingSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            company = self.request.user.company_profile,
            is_active = True
        )
    
    def destroy(self, request, *args, **kwargs):
        # soft delete - never actually delete from the database
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        # return top 5 highest paying jobs
        jobs = JobListing.objects.filter(
            is_active = True
        ).select_related(
            'company', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-salary_max')[:5]

        serializer = JobListingListSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        job = self.get_object()

        # find jobs in same category
        similar_jobs = JobListing.objects.filter(
            is_active = True,
            category = job.category
        ).exclude(
            id = job.id
        ).select_related(
            'company', 'category'
        ).prefetch_related('tags')[:5]

        serializer = JobListingListSerializer(similar_jobs, many = True)
        return Response(serializer.data)

class CategoryListView(GenericAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get(self, request, *args, **kwargs):
        cache_key = "all_categories"
        cached = cache.get(cache_key)

        if cached:
            return Response(cached)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        cache.set(cache_key, data, timeout=3600)

        return Response(data)