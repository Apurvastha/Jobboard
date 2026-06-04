import time
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import JobListing, Category
from .serializers import (
    JobListingListSerializer, 
    JobListingSerializer, 
    CategorySerializer,
)


class JobListCreateView(generics.ListCreateAPIView):
    # override default permission for this specific view
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # build queryset
        queryset = JobListing.objects.filter(
            is_active=True
        ).select_related(
            'company', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-posted_at')

        # filtering from query params
        location = self.request.query_params.get('location')
        job_type = self.request.query_params.get('job_type')
        experience_level = self.request.query_params.get('experience_level')
        is_remote = self.request.query_params.get('is_remote')
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')

        if location:
            queryset= queryset.filter(location__icontains=location)
        if job_type:
            queryset= queryset.filter(job_type=job_type)
        if experience_level:
            queryset= queryset.filter(experience_level=experience_level)
        if is_remote:
            queryset= queryset.filter(is_remote=is_remote.lower()== 'true')
        if search:
            queryset= queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        if category:
            queryset= queryset.filter(category__slug=category)

        return queryset
    
    def get_serializer_class(self):
        if self.request.method=='GET':
            return JobListingListSerializer
        return JobListingSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            company = self.request.user.company_profile,
            is_active = True
        )
class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = JobListingSerializer

    def get_queryset(self):
        return JobListing.objects.select_related(
                'company', 'category'
            ).prefetch_related('tags')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return JobListingListSerializer
        return JobListingSerializer
    
    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False # soft delete - dont actually delete
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CategoryListView(GenericAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get(self, request, *args, **kwargs):
        cache_key = "all_categories"
        cached = cache.get(cache_key)

        if cached:
            return Response(cached)


        # time.sleep(2)  # visualize cache miss for now

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        cache.set(cache_key, data, timeout=3600)

        return Response(data)