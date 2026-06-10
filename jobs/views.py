from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import   AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import JobListingFilter
from .pagination import JobListingPagination
from accounts.permissions import  IsOwnerOrReadOnly, IsCompany
from .models import JobListing, Category
from .serializers import (
    JobListingListSerializer, 
    JobListingSerializer, 
    CategorySerializer,
)

class JobListingViewSet(viewsets.ModelViewSet):
    
    pagination_class = JobListingPagination
    
    # declare filter backends for this viewset
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # django-fiter - uses JobListingFilter
    filterset_class = JobListingFilter

    # SearchFilter - full text search
    # searches across these fields with ?search=python
    search_fields = [
        'title',
        'description',
        'company__name',
    ]

    # OrderingFilter - allow client to sort
    # ?ordering=salary_min -> ascending
    # ?ordering=-salary_min -> descending
    ordering_fields = [
        'posted_at',
        'salary_min',
        'salary_max',
        'title'
    ]

    # default ordering
    ordering = ['-posted_at']

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
        return JobListing.objects.filter(
            is_active = True
        ).select_related(
            'company', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-posted_at')

    
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