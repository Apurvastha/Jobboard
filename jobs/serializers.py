
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
    application_count = serializers.SerializerMethodField()
    salary_range = serializers.SerializerMethodField()

    def get_application_count(self, obj):
        return obj.applications.count()
    
    def get_salary_range(self, obj):
        if obj.salary_min and obj.salary_max:
            return f'${obj.salary_min:,} - ${obj.salary_max:,}'
        return None
    
    def validate_title(self, value):
        # single field validation — same as clean_title() in forms
        if len(value) < 10:
            raise serializers.ValidationError(
                'Title must be at least 10 characters.'
            )
        return value.strip()

    def validate(self, data):
        # cross-field validation — same as clean() in forms
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')

        if salary_min and salary_max and salary_max <= salary_min:
            raise serializers.ValidationError(
                'Maximum salary must be greater than minimum salary.'
            )
        return data


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
            'application_count',
            'salary_range',
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