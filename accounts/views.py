from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from . permissions import IsCandidate
from .serializers import (
    RegisterCandidateSerializer,
    RegisterCompanySerializer,
    UserSerializer,
    CandidateProfileSerializer,
    CompanyProfileSerializer,
)


class RegisterCandidateView(generics.CreateAPIView):
    serializer_class = RegisterCandidateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    
class RegisterCompanyView(generics.CreateAPIView):
    serializer_class = RegisterCompanySerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class CandidateProfileView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request):
       
        if not request.user.has_candidate_profile:
            return Response(
                {'error': 'Profile not found'},
                status= status.HTTP_404_NOT_FOUND
            )
        serializer = CandidateProfileSerializer(
            request.user.candidate_profile
        )
        return Response(serializer.data)
    
    def patch(self, request):
        
        from .models import CandidateProfile
        profile, _ = CandidateProfile.objects.get_or_create(
            user=request.user
        )
        serializer = CandidateProfileSerializer(
            profile,
            data= request.data,
            partial = True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CompanyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_company:
            return Response(
                {'error': 'Only companies have a company profile'},
                status= status.HTTP_403_FORBIDDEN
            )
        
        serializer = CompanyProfileSerializer(
            request.user.company_profile
        )

        return Response(serializer.data)
    
    def patch(self, request):
        if not request.user.is_company:
            return Response(
                {'error': 'Only companies can update company profiles.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CompanyProfileSerializer(
            request.user.company_profile,
            data= request.data,
            partial = True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer