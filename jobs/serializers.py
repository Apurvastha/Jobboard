
from rest_framework import serializers
from .models import JobListing, Category, Tag
from accounts.models import CompanyProfile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['id', 'name', 'website', 'country']


class JobListingSerializer(serializers.ModelSerializer):
    # nested serializers — represent related objects fully
    company = CompanySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    # write-only fields for creating/updating
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=CompanyProfile.objects.all(),
        source='company',
        write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = JobListing
        fields = [
            'id',
            'title',
            'description',
            'company',        # read — returns nested object
            'company_id',     # write — accepts an ID
            'category',       # read
            'category_id',    # write
            'tags',           # read — returns list of objects
            'tag_ids',        # write — accepts list of IDs
            'job_type',
            'experience_level',
            'location',
            'is_remote',
            'salary_min',
            'salary_max',
            'is_active',
            'deadline',
            'posted_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'posted_at', 'updated_at', 'is_active']


class JobListingListSerializer(serializers.ModelSerializer):
    # lighter serializer for list view — no description, no tag details
    company_name = serializers.CharField(source='company.name', read_only=True)
    category_name = serializers.CharField(
        source='category.name',
        read_only=True,
        allow_null=True
    )
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = JobListing
        fields = [
            'id',
            'title',
            'company_name',
            'category_name',
            'job_type',
            'experience_level',
            'location',
            'is_remote',
            'salary_min',
            'salary_max',
            'tags',
            'posted_at',
        ]