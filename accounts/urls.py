from django.contrib import admin
from django.urls import path,include
from .views import RegisterView,LoginView,ProfileView,FollowView

urlpatterns=[
    path('register/', RegisterView.as_view(), name='register'), #회원가입
    path('login/', LoginView.as_view(), name='login'), #로그인
    path('profile/', ProfileView.as_view(), name='profile-view'),#현재 로그인 된 유저 프로파일
    path('follow/<int:pk>/', FollowView.as_view(), name='follow') # 팔로잉 
]