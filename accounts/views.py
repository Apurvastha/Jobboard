from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .throttles import LoginRateThrottle
from .permissions import IsCandidate
from .serializers import (
    CandidateProfileSerializer,
    CompanyProfileSerializer,
    CustomTokenObtainPairSerializer,
    RegisterCandidateSerializer,
    RegisterCompanySerializer,
    UserSerializer,
)



@extend_schema(tags=["Authentication"], summary="Register Candidate")
class RegisterCandidateView(generics.CreateAPIView):
    serializer_class = RegisterCandidateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Authentication"], summary="Register Company")
class RegisterCompanyView(generics.CreateAPIView):
    serializer_class = RegisterCompanySerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Profile"], summary="Get current user")
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary='Get current user',
            responses={200: UserSerializer},
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@extend_schema(tags=["Profile"], summary="Candidate Profile")
class CandidateProfileView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]
    serializer_classes = CandidateProfileSerializer

    @extend_schema(
        summary='Get candidate profile',
        responses={200: CandidateProfileSerializer},
    )
    def get(self, request):

        if not request.user.has_candidate_profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CandidateProfileSerializer(request.user.candidate_profile)
        return Response(serializer.data)

    @extend_schema(
        summary='Update candidate profile',
        request=CandidateProfileSerializer,
        responses={200: CandidateProfileSerializer},
    )
    def patch(self, request):

        from .models import CandidateProfile

        profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
        serializer = CandidateProfileSerializer(
            profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Profile"], summary="Company Profile")
class CompanyProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanyProfileSerializer

    @extend_schema(
        summary='Get company profile',
        responses={200: CompanyProfileSerializer},
    )
    def get(self, request):
        if not request.user.is_company:
            return Response(
                {"error": "Only companies have a company profile"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CompanyProfileSerializer(request.user.company_profile)

        return Response(serializer.data)

    @extend_schema(
        summary='Update company profile',
        request=CompanyProfileSerializer,
        responses={200: CompanyProfileSerializer},
    )
    def patch(self, request):
        if not request.user.is_company:
            return Response(
                {"error": "Only companies can update company profiles."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = CompanyProfileSerializer(
            request.user.company_profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Authentication"], summary="Login")
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]


