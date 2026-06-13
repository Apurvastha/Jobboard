from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db import transaction
from .models import Application
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationStatusUpdateSerializer
)
from accounts.permissions import (
    IsCandidate,
    IsCompany,
    IsJobOwnerForApplication,
    IsApplicationOwner
)


@extend_schema(tags='Applications')
class ApplicationViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'head', 'options']
    
    def get_queryset(self):
        user = self.request.user

        if user.is_candidate:
            return Application.objects.filter(
                candidate=user
            ).select_related(
                'job',
                'job__company',
                'job__category',
                'candidate'
            ).prefetch_related('job__tags').order_by('-applied_at')
        
        if user.is_company:
            return Application.objects.filter(
                job__company = user.company_profile
            ).select_related(
                'job',
                'job__company',
                'candidate'
            ).order_by('-applied_at')
        
        return Application.objects.all().select_related(
            'job', 'job__company', 'candidate'
        ).order_by('-applied_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        if self.action in ['retrieve']:
            return ApplicationDetailSerializer
        if self.action == 'update_status':
            return ApplicationStatusUpdateSerializer
        return ApplicationListSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsCandidate()]
        if self.action == 'update_status':
            return [IsAuthenticated(), IsCompany()]
        return [IsAuthenticated()]
    
    def get_serializer_context(self):
       context = super().get_serializer_context()
       context['request'] = self.request
       return context
    
    @extend_schema(
        summary='Apply to a job listing',
        description='Candidates only. Cannot apply twice to the same job.',
        responses={201: ApplicationDetailSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        # return full detail after creation
        return Response(
            ApplicationDetailSerializer(application).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary='List applications',
        description=(
            'Candidates see their own applications. '
            'Companies see applications for their job listings.'
        ),
        responses={200: ApplicationListSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Get application detail',
        responses={200: ApplicationDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary='Update application status',
        description='Companies only. Changes status: pending → reviewing → accepted/rejected.',
        request=ApplicationStatusUpdateSerializer,
        responses={200: ApplicationDetailSerializer},
    )
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        application = self.get_object()

        # check the company owns this job
        if application.job.company.user != request.user:
            return Response(
                {'error': 'You can only manage applications for your own jobs.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ApplicationStatusUpdateSerializer(
            application,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # return full detail after update
        return Response(
            ApplicationDetailSerializer(application).data
        )

    # disable update and partial_update — use update_status instead
    def update(self, request, *args, **kwargs):
        return Response(
            {'error': 'Use PATCH /applications/{id}/status/ to update status.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
        