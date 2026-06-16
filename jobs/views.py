from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsCompany, IsOwnerOrReadOnly
from applications.serializers import ApplicationListSerializer

from .filters import JobListingFilter
from .models import Category, JobListing
from .pagination import JobListingPagination
from .serializers import (
    CategorySerializer,
    JobListingListSerializer,
    JobListingSerializer,
)


@extend_schema(tags=["Jobs"])
@extend_schema_view(
    list=extend_schema(
        summary="List all active job listings",
        description="Returns paginated list with filtering and search.",
        responses={200: JobListingListSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Create a new job listing",
        description="Only company accounts can create job listings.",
        responses={201: JobListingSerializer, 403: OpenApiTypes.OBJECT},
    ),
    update=extend_schema(
        summary="Update a job listing",
        responses={200: JobListingSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update a job listing",
        responses={200: JobListingSerializer},
    ),
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
        "title",
        "description",
        "company__name",
    ]

    # OrderingFilter - allow client to sort
    # ?ordering=salary_min -> ascending
    # ?ordering=-salary_min -> descending
    ordering_fields = ["posted_at", "salary_min", "salary_max", "title"]

    # default ordering
    ordering = ["-posted_at"]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "featured", "similar"]:
            # read actions - anyone
            return [AllowAny()]

        if self.action == "create":
            # creating - must be a company
            return [IsCompany()]

        if self.action in ["update", "partial_update", "destroy"]:
            # modifying - must be the owner
            return [IsOwnerOrReadOnly()]
        if self.action == "applications":
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return (
            JobListing.objects.filter(is_active=True)
            .select_related("company", "category")
            .prefetch_related("tags")
            .order_by("-posted_at")
        )

    def get_serializer_class(self):
        # list action uses lightweight serializer
        if self.action == "list":
            return JobListingListSerializer
        # everything else uses full serializer
        return JobListingSerializer

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company_profile, is_active=True)

    @extend_schema(
        summary="Get job listing details",
        responses={200: JobListingSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        cache_key = f"job:{pk}"

        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        instance = self.get_object()
        serializer = self.get_serializer(
            instance
        )  # uses get_serializer_class() -> JobListingSerializer
        data = serializer.data

        cache.set(cache_key, data, timeout=1800)
        return Response(data)

    @extend_schema(
        summary="Soft delete a job listing",
        description="Sets is_active=False instead of deleting from database.",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        # soft delete - never actually delete from the database
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Get featured job listings",
        description="Returns top 5 highest paying active jobs.",
        responses={200: JobListingListSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def featured(self, request):
        cache_key = "featured_jobs"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        # return top 5 highest paying jobs
        jobs = (
            JobListing.objects.filter(is_active=True)
            .select_related("company", "category")
            .prefetch_related("tags")
            .order_by("-salary_max")[:5]
        )

        serializer = JobListingListSerializer(jobs, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=3600)
        return Response(data)

    @extend_schema(
        summary="Get similar job listings",
        description="Returns jobs in the same category as the specified job.",
        responses={200: JobListingListSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def similar(self, request, pk=None):
        job = self.get_object()

        # find jobs in same category
        similar_jobs = (
            JobListing.objects.filter(is_active=True, category=job.category)
            .exclude(id=job.id)
            .select_related("company", "category")
            .prefetch_related("tags")[:5]
        )

        serializer = JobListingListSerializer(similar_jobs, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get applications for a job listing",
        description="Companies only. Returns all applications for this job.",
        responses={200: ApplicationListSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="applications")
    def applications(self, request, pk=None):
        from applications.models import Application
        from applications.serializers import ApplicationListSerializer

        job = self.get_object()

        # only the company that owns this job can see its applications
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not request.user.is_company:
            return Response(
                {"error": "Only company accounts can view applications."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if job.company.user != request.user:
            return Response(
                {"error": "You can only view applications for your own jobs."},
                status=status.HTTP_403_FORBIDDEN,
            )

        applications = (
            Application.objects.filter(job=job)
            .select_related(
                "candidate",
                "job",
            )
            .order_by("-applied_at")
        )

        # filter by status if provided
        status_filter = request.query_params.get("status")
        if status_filter:
            applications = applications.filter(status=status_filter)

        serializer = ApplicationListSerializer(applications, many=True)
        return Response(
            {
                "job": job.title,
                "total": applications.count(),
                "results": serializer.data,
            }
        )


@extend_schema(
    tags=["Jobs"],
    summary="List all job categories",
    description="Returns cached list of all job categories. Cache refreshes every hour.",
    responses={200: CategorySerializer(many=True)},
)
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
