from django.contrib import admin
from django.urls import path,include
from .views import RegisterView,LoginView,ProfileDetailView

urlpatterns=[
    path('register/', RegisterView.as_view(), name='register'), #회원가입
    path('login/', LoginView.as_view(), name='login'), #로그인
    path('profile/', ProfileDetailView.as_view(), name='profile-detail')
]