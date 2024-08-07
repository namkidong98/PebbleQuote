
from rest_framework import serializers
from .models import Quote,Comment
from accounts.models import User
# from accounts.serializers import UserSerializer # 이렇게 사용하면 순환 임포트가 발생

class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ['id', 'content', 'description', 'author', 'image', 'created_at','like_count','user_author', 'quote_viewers']

class QuoteForProfileSerializer(serializers.ModelSerializer):  #accounts profile-view를 위한 Serializer-필요한 필드만 보여주게 함(ex.author은 중복되니 삭제)
    class Meta:
        model = Quote
        fields = ['id', 'content', 'description', 'created_at', 'like_count']

class CommentSerializer(serializers.ModelSerializer):
    # user = serializers.ReadOnlyField(source='user.nickname')
    # user = UserSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'quote', 'created_at', 'user', 'content']

    def get_user(self, obj):
        from accounts.serializers import UserSerializer # 순환 임포트를 피하기 위한 로컬 임포트
        user = obj.user
        return UserSerializer(user).data