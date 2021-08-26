from rest_framework import serializers
from .models import Post, Emotion

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('post','id')
        extra_kwargs = {
            'post': {'write_only': True},
        }


class EmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emotion
        fields = ('post', 'user', 'emotion')