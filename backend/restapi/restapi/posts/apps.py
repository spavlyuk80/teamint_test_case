from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'
    # from .models import Post, Emotion
    # from django.contrib.auth.models import User