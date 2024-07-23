from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'password', 'nickname', 'name', 'age', 'sex', 'birth', 'phone',
            'followers', 'following', 'registered_quotes', 'liked_quotes'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nickname=validated_data['nickname'],
            name=validated_data['name'],
            age=validated_data['age'],
            sex=validated_data['sex'],
            birth=validated_data['birth'],
            phone=validated_data['phone']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()