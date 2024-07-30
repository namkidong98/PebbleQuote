from django.db import models
from accounts.models import User, UserManager 
from django.conf import settings

class Quote(models.Model):
    # 필수 입력 필드
    content = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    author = models.CharField(max_length=100)      # 명언 발화자(유명인물 + 명언 직접 생성한 유저들 닉네임)
    
    # 자동 생성 필드
    image = models.ImageField(upload_to='quotes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)
    
    #명언 직접 생성한 유저들
    user_author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='registered_quotes')

    def __str__(self):
        return self.content
    
class Comment(models.Model):
    quote = models.ForeignKey(Quote, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content