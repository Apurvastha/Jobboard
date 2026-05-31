from rest_framework import serializers
from .models import Application
from jobs.serializers import JobListingListSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobListingListSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        source='job',
        write_only=True,
        queryset=__import__(
            'jobs.models', fromlist=['JobListing']
        ).JobListing.objects.filter(is_active=True)
    )
    candidate_email = serializers.EmailField(
        source='candidate.email',
        read_only=True
    )

    class Meta:
        model = Application
        fields = [
            'id',
            'job',
            'job_id',
            'candidate_email',
            'status',
            'cover_letter',
            'applied_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'applied_at',
            'updated_at',
            'candidate_email',
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request:
            already_applied = Application.objects.filter(
                candidate=request.user,
                job=data.get('job')
            ).exists()
            if already_applied:
                raise serializers.ValidationError(
                    'You have already applied to this job.'
                )
        return data