from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from quote.serializers import QuoteSerializer, QuoteForProfileSerializer

from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'password', 'nickname', 'like_quotes'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nickname=validated_data['nickname'],
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    
# class SimpleUserSerializer(serializers.ModelSerializer):
#     registered_quotes = QuoteForProfileSerializer(many=True, read_only=True)  # 팔로잉 한 유저가 등록한 명언들을 프로파일 뷰에서 간단하게 보여주기 위해 만듦
#     class Meta:
#         model = User
#         fields = ['id', 'nickname','registered_quotes']

class ProfileSerializer(serializers.ModelSerializer):
    like_quotes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    registered_quotes = QuoteForProfileSerializer(many=True, read_only=True) # Quote에 foreign key 로 들어간 user id 역참조
    followings =serializers.PrimaryKeyRelatedField(many=True, read_only=True) #팔로잉 한 유저 id 만 저장
    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True) #팔로워 한 유저 id 만 저장
    

    class Meta:
        model = User
        fields = ['nickname', 'like_quotes', 'email','registered_quotes','followings', 'followers', 'following_count','follower_count']
