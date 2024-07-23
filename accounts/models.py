from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField
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
    name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    sex = models.CharField(max_length=6, choices=SEX_CHOICES)
    birth = models.DateField()
    phone_regex = RegexValidator(
        regex=r'^010-\d{4}-\d{4}$',
        message="Phone number must be entered in the format: '010-0000-0000'."
    )
    phone = models.CharField(validators=[phone_regex], max_length=13)

    followers = ArrayField(models.PositiveIntegerField(), default=list, blank=True)
    following = ArrayField(models.PositiveIntegerField(), default=list, blank=True)
    registered_quotes = ArrayField(models.PositiveIntegerField(), default=list, blank=True)
    liked_quotes = ArrayField(models.PositiveIntegerField(), default=list, blank=True)
    duplicate_quotes=ArrayField(models.PositiveIntegerField(), default=list, blank=True) #추천받은 명언 리스트 저장(중복 추천 방지)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email' #사용자 이름으로 이메일 사용
    REQUIRED_FIELDS = ['nickname', 'name', 'age', 'sex', 'birth', 'phone']

    def __str__(self):
        return self.email
    
    def add_duplicate_quote(self,quote_id):
        if quote_id not in self.duplicate_quotes:
            self.duplicate_quotes.append(quote_id)
            self.save()

            


