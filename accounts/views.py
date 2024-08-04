
from django.views import View
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, LoginSerializer, ProfileSerializer, ProfileUpdateSerializer
from django.shortcuts import get_object_or_404
import os
from dotenv import load_dotenv
from django.conf import settings
import requests
from .models import User
import jwt
import logging
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponseBadRequest


load_dotenv()

User = get_user_model()

class RegisterView(generics.ListCreateAPIView):
    # generics.CreateAPIView는 POST요청만을 허용
    # ListCreateAPIView로 변경하여 GET 요청으로 유저 조회 기능 추가
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
def KakaoLoginTest(request):
    app_rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
    redirect_uri = 'http://127.0.0.1:8000/accounts/kakao/callback/'  #변경
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code")


# class KakaoLoginView(View):    
#     def get(self,request):
#         app_rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
#         redirect_uri = 'http://127.0.0.1:8000/accounts/kakao/callback/'  #변경
#         return redirect(
#             f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code")
#     @csrf_exempt
#     def post(self,request):
#         app_rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
#         redirect_uri = 'http://127.0.0.1:8000/accounts/kakao/callback/'  #변경
#         return redirect(
#             f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code")




@csrf_exempt
def Kakaocallback(request):
    code = request.GET.get('code')
    if not code:
        logging.error("Authorization code is missing")
        return HttpResponseBadRequest("Authorization code is missing")

    token_url = 'https://kauth.kakao.com/oauth/token'
    redirect_uri = 'http://127.0.0.1:8000/accounts/kakao/callback/'
    client_id = os.environ.get("KAKAO_REST_API_KEY")

    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code': code
    }
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    }
    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    logging.debug(f"Token response status: {token_response.status_code}")
    logging.debug(f"Token response data: {token_response.text}")

    if token_response.status_code != 200:
        logging.error(f"Token request failed: {token_response.text}")
        return HttpResponseBadRequest("Failed to fetch token from Kakao")

    token_json = token_response.json()
    access_token = token_json.get('access_token')
    if not access_token:
        logging.error("Access token is missing in the response")
        return HttpResponseBadRequest("Access token is missing")

    user_info_url = 'https://kapi.kakao.com/v2/user/me'
    user_info_headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    }
    user_info_response = requests.get(user_info_url, headers=user_info_headers)
    logging.debug(f"User info response status: {user_info_response.status_code}")
    logging.debug(f"User info response data: {user_info_response.text}")

    if user_info_response.status_code != 200:
        logging.error(f"User info request failed: {user_info_response.text}")
        return HttpResponseBadRequest("Failed to fetch user info from Kakao")

    user_info_json = user_info_response.json()
    kakao_account = user_info_json.get('kakao_account')
    if not kakao_account:
        logging.error("kakao_account is missing in the user info response")
        return HttpResponseBadRequest("Failed to retrieve Kakao account information")

    kakao_email = kakao_account.get('email')
    kakao_profile = kakao_account.get('profile')
    kakao_nickname = kakao_profile.get('nickname')
    kakao_profile_image_url = kakao_profile.get('profile_image_url') #프사

    if User.objects.filter(email=kakao_email).exists():
        user = User.objects.get(email=kakao_email)
    else:
        user = User.objects.create(
            email=kakao_email,
            nickname=kakao_nickname,
            # profile_image=kakao_profile_image
        )

        if kakao_profile_image_url:
            image_response = requests.get(kakao_profile_image_url)
            if image_response.status_code == 200:
                image_name = f'{user.id}_profile.jpg'
                user.profile_image.save(image_name, ContentFile(image_response.content))
            else:
                logging.error(f"Failed to download profile image from {kakao_profile_image_url}")


    jwt_token = jwt.encode({'email': user.email}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # #redirect uri설정 (프론트엔드 URL로 변경)
    # frontend_redirect_uri = ''

    response_data = {
        'email': user.email,
        'token': jwt_token,
        'exist': User.objects.filter(email=kakao_email).exists()
    }

    return JsonResponse(response_data)
    #프론트엔드로 리다이렉트하면서 토큰과 사용자 정보를 쿼리 파라미터로 전달
    # redirect_url = f"{frontend_redirect_uri}?email={response_data['email']}&token={response_data['token']}&exist={response_data['exist']}"
    # return redirect(redirect_url)
        