# accounts/views.py
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .serializers import UserSerializer, LoginSerializer, ProfileSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  #인증 불필요


class LoginView(APIView):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


def kakao_login(request):
    app_rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
    redirect_uri = "http://localhost:8000/users/login/kakao/callback"  #변경
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={'api 키 값'}&redirect_uri={'넘겨주는 url값'}&response_type=code")
    
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 현재 인증된 사용자
        user = request.user
        # 사용자 프로필 직렬화
        serializer = ProfileSerializer(user)
        # 직렬화된 데이터 응답
        return Response(serializer.data, status=status.HTTP_200_OK)


