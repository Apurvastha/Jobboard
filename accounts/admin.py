from django.contrib import admin
from django.db.models import Count
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from jobs.admin import JobListingInline
from .models import User, CompanyProfile, CandidateProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    #extend the default UserAdmin to show your custom fields
    list_display = [
        'email',
        'username',
        'role',
        'is_active',
        'is_staff',
        'date_joined',
    ]

    list_filter = ['role', 'is_active', 'is_staff']
    search_filters = ['email', 'username']

    #add role to the fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role',{
            'fields': ['role']
        }

        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            'Role', {
                'fields': ['role']
            }
        ),
    )

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'country', 'founded_year', 'job_count']
    search_fields = ['name', 'user__email']
    list_select_related = ['user']
    inlines = [JobListingInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            job_count=Count('job_listings')
        )

    def job_count(self, obj):
        return obj.job_count

    job_count.short_description = 'Jobs Posted'
    job_count.admin_order_field = 'job_count'


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'years_of_experience']
    search_fields = ['user__email']
    list_select_related = ['user']