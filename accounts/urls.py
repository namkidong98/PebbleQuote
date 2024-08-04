from django.urls import path,include
from .views import RegisterView,LoginView,ProfileView,FollowView,KakaoLoginTest, Kakaocallback
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('register/', RegisterView.as_view(), name='register'), #회원가입
    path('login/', LoginView.as_view(), name='login'), #로그인
    path('profile/', ProfileView.as_view(), name='profile-view'),#현재 로그인 된 유저 프로파일
    path('follow/<int:pk>/', FollowView.as_view(), name='follow'), # 팔로잉 

    # path('kakao/login/', KakaoLoginView.as_view(), name='kakao_login'),
    path('kakao/login/', KakaoLoginTest, name='kakao_login'),
    # path('kakao/callback/', KakaoCallbackView.as_view(), name='kakao_callback'),
    path('kakao/callback/', Kakaocallback, name='kakao_callback')
]