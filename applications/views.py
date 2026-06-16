from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsCandidate, IsCompany
from .models import Application
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationDetailSerializer,
    ApplicationListSerializer,
    ApplicationStatusUpdateSerializer,
)


@extend_schema(tags=["Applications"])
@extend_schema_view(
    list=extend_schema(
        summary="List applications",
        description=(
            "Candidates see their own applications. "
            "Companies see applications for their job listings."
        ),
        responses={200: ApplicationListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Get application detail",
        responses={200: ApplicationDetailSerializer},
    ),
)
class ApplicationViewSet(viewsets.ModelViewSet):
    # only allow safe methods + POST and PATCH
    # PUT is excluded entirely
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user

        if user.is_candidate:
            return (
                Application.objects.filter(candidate=user)
                .select_related("job", "job__company", "job__category", "candidate")
                .prefetch_related("job__tags")
                .order_by("-applied_at")
            )

        if user.is_company:
            return (
                Application.objects.filter(job__company=user.company_profile)
                .select_related("job", "job__company", "candidate")
                .order_by("-applied_at")
            )

        # admin sees all
        return (
            Application.objects.all()
            .select_related("job", "job__company", "candidate")
            .order_by("-applied_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return ApplicationCreateSerializer
        if self.action == "retrieve":
            return ApplicationDetailSerializer
        if self.action == "update_status":
            return ApplicationStatusUpdateSerializer
        return ApplicationListSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsCandidate()]
        if self.action == "update_status":
            return [IsAuthenticated(), IsCompany()]
        return [IsAuthenticated()]

    @extend_schema(
        summary="Apply to a job listing",
        description="Candidates only. Cannot apply twice to the same job.",
        responses={201: ApplicationDetailSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        return Response(
            ApplicationDetailSerializer(
                application,
                context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Update application status",
        description="Companies only. Changes status: pending → reviewing → accepted/rejected.",
        request=ApplicationStatusUpdateSerializer,
        responses={200: ApplicationDetailSerializer},
    )
    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        application = self.get_object()

        if application.job.company.user != request.user:
            return Response(
                {"error": "You can only manage applications for your own jobs."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ApplicationStatusUpdateSerializer(
            application,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            ApplicationDetailSerializer(
                application,
                context={"request": request}
            ).data
        )

    # hide from Swagger and return 405 — status update goes to /{id}/status/
    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"error": "Use PATCH /applications/{id}/status/ to update status."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return Response(
            {"error": "Use PATCH /applications/{id}/status/ to update status."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        return Response(
            {"error": "Applications cannot be deleted."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )