from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, CompanyProfile, CandidateProfile


class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = [
            'id',
            'bio',
            'resume_url',
            'years_of_experience',
            'skills',
        ]


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = [
            'id',
            'name',
            'website',
            'description',
            'country',
            'founded_year',
        ]


class UserSerializer(serializers.ModelSerializer):
    candidate_profile = CandidateProfileSerializer(read_only=True)
    company_profile = CompanyProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'is_active',
            'date_joined',
            'candidate_profile',
            'company_profile',
        ]
        read_only_fields = ['id', 'date_joined', 'is_active']


class RegisterCandidateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match.'}
            )
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.Role.CANDIDATE,
        )
        return user


class RegisterCompanySerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True)
    company_name = serializers.CharField(max_length=200, write_only=True)
    website = serializers.URLField(required=False, write_only=True)
    country = serializers.CharField(
        max_length=100,
        default='Japan',
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password2',
            'company_name',
            'website',
            'country',
        ]

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match.'}
            )
        return data

    def create(self, validated_data):
        company_name = validated_data.pop('company_name')
        website = validated_data.pop('website', '')
        country = validated_data.pop('country', 'Japan')
        validated_data.pop('password2')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.Role.COMPANY,
        )

        CompanyProfile.objects.create(
            user=user,
            name=company_name,
            website=website,
            country=country,
        )

        return user