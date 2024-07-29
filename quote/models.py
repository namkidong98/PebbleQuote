from django.db import models
from accounts.models import User, UserManager 
from django.conf import settings

class Quote(models.Model):
    # 필수 입력 필드
    content = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    author = models.CharField(max_length=100)      # 해당 명언의 원발화자
    
    # 자동 생성 필드
    image = models.ImageField(upload_to='quotes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)
    
    #직접 명언 생성한 유저들
    user_author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_author')

    def __str__(self):
        return self.content
    
class Comment(models.Model):
    quote = models.ForeignKey(Quote, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content