from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from quote.serializers import QuoteSerializer, QuoteForProfileSerializer

from accounts.models import User
from quote.models import Quote

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'password', 'nickname'
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
    
    
class SimpleUserSerializer(serializers.ModelSerializer):
    registered_quotes = QuoteForProfileSerializer(many=True, read_only=True)  # 팔로잉 한 유저가 등록한 명언들을 프로파일 뷰에서 간단하게 보여주기 위해 만듦
    class Meta:
        model = User
        fields = ['id', 'nickname','registered_quotes']

class ProfileSerializer(serializers.ModelSerializer):
    like_quotes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    registered_quotes = QuoteForProfileSerializer(many=True, read_only=True) # Quote에 foreign key 로 들어간 user id 역참조
    # followings =serializers.PrimaryKeyRelatedField(many=True, read_only=True) #팔로잉 한 유저 id 만 저장
    followings = SimpleUserSerializer(many=True, read_only=True) # 팔로잉 한 유저 간단한 정보를 담아서 보냄
    followers = serializers.PrimaryKeyRelatedField(many=True, read_only=True) #팔로워 한 유저 id 만 저장

    class Meta:
        model = User
        fields = ['nickname', 'like_quotes', 'email','registered_quotes','followings', 'followers', 'following_count','follower_count']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=False)
    new_password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['nickname', 'email', 'current_password', 'new_password', 'new_password_confirm']

    def validate(self, data):
        user = self.instance
        if not user.check_password(data.get('current_password')):
            raise serializers.ValidationError("Current password is incorrect.")
        if 'new_password' in data or 'new_password_confirm' in data:
            if data.get('new_password') != data.get('new_password_confirm'):
                raise serializers.ValidationError("The new passwords do not match.")
        return data

    def update(self, instance, validated_data):
        current_nickname = instance.nickname #현재 닉네임 
        validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('new_password_confirm', None)
        instance = super().update(instance, validated_data) #닉네임 수정
        if new_password:
            instance.set_password(new_password)
            instance.save()
        if current_nickname != instance.nickname:
            Quote.objects.filter(user_author=instance).update(author=instance.nickname) #quote author 바뀐 닉네임으로 변경
        
        return instance
    
    
    
