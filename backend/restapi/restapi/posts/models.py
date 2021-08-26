from django.db import models
from django.contrib.auth.models import User


__all__ = ['Post', 'Emotion']


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    post_timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)  # may be not necessary
    post = models.TextField(max_length=8000)
    deleted = models.BooleanField(default=False) # just in case we need userdata

    def __str__(self) -> str:
        return f"{self.author} - {self.post_timestamp}"


class Emotion(models.Model):
    # TODO: create indices

    class EmotionChoices:
        LIKE = 1
        DISLIKE = -1
        CHOICES = [
            (LIKE, 'Like'),
            (DISLIKE, 'Dislike'),
        ]

    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    emotion = models.IntegerField(choices=EmotionChoices.CHOICES)

    class Meta:

        # make sure user-emotion-post is unique
        constraints = [
            models.UniqueConstraint(fields=['post', 'user', 'emotion'], 
                                    name='unique_emotion'),
        ]

    def __str__(self) -> str:
        return f"{self.post}-{self.user}-{self.emotion}"