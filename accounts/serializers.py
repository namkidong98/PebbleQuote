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

class ProfileSerializer(serializers.ModelSerializer):
    like_quotes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    registered_quotes = QuoteForProfileSerializer(many=True, read_only=True) # Quote에 foreign key 로 들어간 user id 역참조 

    class Meta:
        model = User
        fields = ['nickname', 'like_quotes', 'email','registered_quotes']
