# applications/admin.py
from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    list_display = [
        'candidate',
        'job',
        'status',
        'applied_at',
    ]

    list_filter = ['status', 'applied_at']

    search_fields = [
        'candidate__email',
        'job__title',
        'job__company__name',
    ]

    # allow changing status directly in list view
    list_editable = ['status']

    readonly_fields = ['applied_at', 'updated_at']

    # optimise queries
    list_select_related = ['candidate', 'job', 'job__company']

    list_per_page = 50

    # bulk actions for status changes
    actions = [
        'mark_reviewing',
        'mark_rejected',
        'mark_accepted',
    ]

    def mark_reviewing(self, request, queryset):
        count = queryset.update(status='reviewing')
        self.message_user(request, f'{count} applications marked as reviewing.')
    mark_reviewing.short_description = 'Mark as reviewing'

    def mark_rejected(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'{count} applications marked as rejected.')
    mark_rejected.short_description = 'Mark as rejected'

    def mark_accepted(self, request, queryset):
        count = queryset.update(status='accepted')
        self.message_user(request, f'{count} applications marked as accepted.')
    mark_accepted.short_description = 'Mark as accepted'