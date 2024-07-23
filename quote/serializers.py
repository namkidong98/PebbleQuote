# quote/serializers.py

from rest_framework import serializers
from .models import Quote, Tag
from accounts.models import User

class QuoteSerializer(serializers.ModelSerializer):
    registrant = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    tag = serializers.SlugRelatedField(slug_field='name', queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Quote
        fields = ['content', 'description', 'author', 'registrant', 'tag', 'image', 'likes', 'comments', 'created_at']

    def create(self, validated_data):
        tags_data = validated_data.pop('tag')
        quote = Quote.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_data)
            quote.tag.add(tag)
        return quote

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tag')
        instance.content = validated_data.get('content', instance.content)
        instance.description = validated_data.get('description', instance.description)
        instance.author = validated_data.get('author', instance.author)
        instance.registrant = validated_data.get('registrant', instance.registrant)
        instance.image = validated_data.get('image', instance.image)
        instance.likes = validated_data.get('likes', instance.likes)
        instance.comments = validated_data.get('comments', instance.comments)
        instance.save()

        instance.tag.clear()
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_data)
            instance.tag.add(tag)
        return instance
