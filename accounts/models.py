from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError(_('이메일을 입력하세요'))
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db) #데이터베이스에 저장
        return user
    #슈퍼유저 생성
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email,password,**extra_fields)

class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    nickname = models.CharField(max_length=50)
    
    like_quotes = models.ManyToManyField(settings.QUOTE_MODEL, blank=True, related_name='like_quotes') #좋아요 한 명언목록
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers') #팔로잉 다대다 #self 인 이유는 유저끼리 이루어지는 것이기 때문
    follower_count = models.PositiveIntegerField(default=0)     # 팔로워 수
    following_count = models.PositiveIntegerField(default=0)    # 팔로잉 수

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email' #사용자 이름으로 이메일 사용
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.email