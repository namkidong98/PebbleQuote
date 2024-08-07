from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.http import JsonResponse

from .serializers import UserSerializer, LoginSerializer, ProfileSerializer, ProfileUpdateSerializer
from .models import User
import os, logging, requests
from dotenv import load_dotenv

load_dotenv()

User = get_user_model()

SERVER_IP = os.environ.get("SERVER_IP")
KAKAO_REDIRECT_URL = os.environ.get("KAKAO_REDIRECT_URL")

# 모든 유저의 프로필을 확인할 수 있는 리스트
class AllUserProfileView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

class RegisterView(generics.ListCreateAPIView):
    # generics.CreateAPIView는 POST요청만을 허용
    # ListCreateAPIView로 변경하여 GET 요청으로 유저 조회 기능 추가
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  #인증 불필요

class LoginView(APIView):
    permission_classes = [AllowAny]

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
            refresh = RefreshToken.for_user(user)
            token_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(token_data, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): # 유저 프로필 창에 들어갈 내용
        # 현재 인증된 사용자
        user = request.user
        # 사용자 프로필 직렬화
        serializer = ProfileSerializer(user)
        # 직렬화된 데이터 응답
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):     # 유저 정보 수정 기능
        user = request.user     # 인증된 유저
        serializer = ProfileUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):  # 탈퇴 기능
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_to_follow = get_object_or_404(User, pk=pk)
        current_user = request.user

        if user_to_follow in current_user.followings.all(): #팔로워 하려는 유저가 팔로잉에 이미 있는데 다시 팔로우 버튼 누르면
            current_user.followings.remove(user_to_follow) #삭제 (언팔한 거임)
            current_user.following_count -= 1 #현재 유저 팔로잉 수 줄어들고
            user_to_follow.follower_count -= 1 #팔로우 하려했던 유저는 팔로워 수 줄어들고
            current_user.save()
            user_to_follow.save()
            return Response({'팔로우를 취소했습니다.'}, status=status.HTTP_200_OK)
        else:
            current_user.followings.add(user_to_follow) #팔로워 하려는 유저가 현재 팔로잉 목록에 없는데 팔로우 버튼 누를 시 팔로우 됨
            current_user.following_count += 1 #현재 유저 팔로잉 수 늘어나고
            user_to_follow.follower_count += 1 #팔로워하려했던 유저 팔로워 수 늘어나고
            current_user.save()
            user_to_follow.save()
            return Response({ '팔로우했습니다.'}, status=status.HTTP_200_OK)

@csrf_exempt
def KakaoLogin(request):
    app_rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
    # redirect_uri = 'http://127.0.0.1:8000/accounts/kakao/callback/'   # 변경
    # redirect_uri='http://localhost:3000/auth/callback/'
    redirect_uri='https://hackathonpebble.vercel.app/auth/callback/'    # 프론트 배포주소
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code")

@csrf_exempt
def Kakaocallback(request):
    code = request.GET.get('code')
    token_url = 'https://kauth.kakao.com/oauth/token'
    # redirect_uri='http://localhost:3000/auth/callback/'
    redirect_uri='https://hackathonpebble.vercel.app/auth/callback/'   # 프론트 배포주소
    client_id = os.environ.get("KAKAO_REST_API_KEY")
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code': code,
    }
    headers={
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    token_response = requests.post(token_url, data=data,headers=headers)
    token_json=token_response.json()
    access_token=token_json.get("access_token")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info_json = user_info_response.json()

    kakao_account = user_info_json.get('kakao_account')
    kakao_email = kakao_account.get('email')
    kakao_profile = kakao_account.get('profile')
    kakao_nickname = kakao_profile.get('nickname')
    kakao_profile_image_url = kakao_profile.get('profile_image_url')

    if User.objects.filter(email=kakao_email).exists():
        user = User.objects.get(email=kakao_email)
    else:
        user = User.objects.create(
            email=kakao_email,
            nickname=kakao_nickname,
        )
        if kakao_profile_image_url:
            image_response = requests.get(kakao_profile_image_url)
            if image_response.status_code == 200:
                image_name = f'{user.id}_profile.jpg'
                user.profile_image.save(image_name, ContentFile(image_response.content))
            else:
                logging.error(f"Failed to download profile image from {kakao_profile_image_url}")

    refresh = RefreshToken.for_user(user)
    token_data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    return JsonResponse(token_data)