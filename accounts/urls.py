from django.urls import path
from .views import RegisterView, LoginView, ProfileView, FollowView, AllUserProfileView
from .views import KakaoLogin, Kakaocallback

urlpatterns=[
    path('register/', RegisterView.as_view(), name='register'),     # 회원가입
    path('login/', LoginView.as_view(), name='login'),              # 로그인
    path('profile/', ProfileView.as_view(), name='profile-view'),   # 현재 로그인 된 유저 프로파일
    path('follow/<int:pk>/', FollowView.as_view(), name='follow'),  # 팔로잉 
    path('list/', AllUserProfileView.as_view(), name='list'),       # 모든 유저의 정보를 나열하기 위해
    path('kakao/login/', KakaoLogin, name='kakao_login'),
    path('kakao/callback/', Kakaocallback, name='kakao_callback'),
    
]