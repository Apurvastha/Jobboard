# jobs/admin.py
from django.contrib import admin
from django.db.models import Count

from .models import Category, JobListing, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # columns shown in the list view
    list_display = ["name", "slug", "job_count"]

    # makes the slug auto-fill from the name as you type
    prepopulated_fields = {"slug": ("name",)}

    # search box at the top — searches these fields
    search_fields = ["name"]

    # add job count as a custom column
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(job_count=Count("job_listings"))

    # custom column method
    def job_count(self, obj):
        return obj.job_count

    job_count.short_description = "Total Jobs"
    job_count.admin_order_field = "job_count"  # makes column sortable


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    # columns in list view
    list_display = [
        "title",
        "company",
        "category",
        "job_type",
        "experience_level",
        "location",
        "is_remote",
        "salary_min",
        "salary_max",
        "is_active",
        "posted_at",
    ]

    # filters on the right sidebar
    list_filter = [
        "is_active",
        "is_remote",
        "job_type",
        "experience_level",
        "category",
        "location",
    ]

    # search box
    search_fields = [
        "title",
        "description",
        "company__name",  # search across ForeignKey
    ]

    # click to toggle is_active directly in the list
    list_editable = ["is_active"]

    # fields that cannot be edited
    readonly_fields = ["posted_at", "updated_at"]

    # optimise queries — avoids N+1 in admin list view
    list_select_related = ["company", "category"]

    # how many rows per page
    list_per_page = 25

    # organise the detail/edit form into sections
    fieldsets = [
        (
            "Job Information",
            {
                "fields": [
                    "title",
                    "description",
                    "company",
                    "category",
                    "tags",
                ]
            },
        ),
        (
            "Job Details",
            {
                "fields": [
                    "job_type",
                    "experience_level",
                    "location",
                    "is_remote",
                    "deadline",
                ]
            },
        ),
        (
            "Salary",
            {
                "fields": [
                    "salary_min",
                    "salary_max",
                ]
            },
        ),
        (
            "Status",
            {
                "fields": [
                    "is_active",
                    "posted_at",
                    "updated_at",
                ]
            },
        ),
    ]

    # custom bulk action
    actions = ["activate_jobs", "deactivate_jobs"]

    def activate_jobs(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} jobs activated.")

    activate_jobs.short_description = "Activate selected jobs"

    def deactivate_jobs(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} jobs deactivated.")

    deactivate_jobs.short_description = "Deactivate selected jobs"
