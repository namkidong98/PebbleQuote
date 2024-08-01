from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly,IsAuthenticated
from .serializers import UserSerializer, LoginSerializer, ProfileSerializer
from django.shortcuts import get_object_or_404
import os

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
        

