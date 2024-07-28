from django.db import models
# from django.contrib.auth import get_user_model
from accounts.models import User,UserManager 
from django.conf import settings



class Quote(models.Model):
    content = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    author = models.CharField(max_length=100)      # 해당 명언의 원발화자
  

    image = models.ImageField(upload_to='quotes/', null=True, blank=True)
    # liked_by = models.ManyToManyField(
    #     User,
    #     related_name='liked_quotes',
    #     blank=True
    # )
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.content
    

# class Tag(models.Model):
#     name=models.CharField(max_length=50)

#     def __str__(self):
#         return self.name
    
