
from rest_framework import serializers
from .models import Quote,Comment
from accounts.models import User

class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ['id', 'content', 'description', 'author', 'image', 'created_at','like_count','user_author', 'quote_viewers']

class QuoteForProfileSerializer(serializers.ModelSerializer):  #accounts profile-view를 위한 Serializer-필요한 필드만 보여주게 함(ex.author은 중복되니 삭제)
    class Meta:
        model = Quote
        fields = ['id', 'content', 'description', 'image', 'created_at', 'like_count']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    class Meta:
        model = Comment
        fields = ['id', 'quote', 'created_at', 'user', 'content']




