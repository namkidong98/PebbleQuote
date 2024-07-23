from django.db import models
# from django.contrib.auth import get_user_model
from accounts.models import User,UserManager 


class Quote(models.Model):
    content = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    author = models.CharField(max_length=100)      # 해당 명언의 원발화자
    registrant = models.ForeignKey(User, on_delete=models.CASCADE)  # 작성자(User)의 외래 키
    tag = models.ManyToManyField('Tag')
    image = models.ImageField(upload_to='quotes/', null=True, blank=True)
    likes = models.IntegerField(default=0)
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
    

class Tag(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
