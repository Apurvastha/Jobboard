from rest_framework import serializers
from .models import Application
from jobs.serializers import JobListingListSerializer
from accounts.serializers import UserSerializer


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
    
class ApplicationCreateSerializer(serializers.ModelSerializer):
    """only accepts job and cover_letter - candidate is set from request.user"""

    class Meta:
        model = Application
        fields = ['id','job', 'cover_letter', 'status', 'applied_at']
        read_only_fields = ['id', 'status', 'applied_at']

    def validate_job(self, job):
        # job must be active
        if not job.is_active:
            raise serializers.ValidationError(
                'This job listing is no longer active'
            )
        return job
    
    def validate(self, data):
        request = self.context.get('request')
        if request:
            # check for duplicates
            already_applied = Application.objects.filter(
                candidate= request.user,
                job=data.get('job')
            ).exists()
            if already_applied:
                raise serializers.ValidationError(
                    'You have already applied to this job.'
                )
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        return Application.objects.create(
            candidate = request.user,
            **validated_data
        )
    
class ApplicationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views.
    Candidates see their applications with job summary.
    """
    job = JobListingListSerializer(read_only=True)
    candidate_email = serializers.EmailField(
        source='candidate.email',
        read_only=True
    )

    class Meta:
        model = Application
        fields = [
            'id',
            'job',
            'candidate_email',
            'status',
            'applied_at',
            'updated_at'
        ]
        read_only_fields = fields

class ApplicationDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for detial view.
    Includes cover letter and full job details.
    """
    job=JobListingListSerializer(read_only=True)
    candidate_email = serializers.EmailField(
        source='candidate.email',
        read_only=True
    )
    candidate_username = serializers.CharField(
        source='candidate.username',
        read_only=True
    )
    class Meta:
        model = Application
        fields = [
            'id',
            'job',
            'candidate_email',
            'candidate_username',
            'status',
            'cover_letter',
            'applied_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'job',
            'candidate_email',
            'candidate_username',
            'applied_at',
            'updated_at',
        ]

class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    only status is writable - nothing else.
    """
    class Meta:
        model = Application
        fields = ['id', 'status', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def validate_status(self, value):
        valid_statuses = [s[0] for s in Application.Status.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f'Invalid status. Must be one of: {valid_statuses}'
            )
        return value
    

        

    