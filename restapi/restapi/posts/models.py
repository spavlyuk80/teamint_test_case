from django.db import models


__all__ = ['Post', 'Emotion']

user_model = 'users.Profile'

class Post(models.Model):
    author = models.ForeignKey(user_model, on_delete=models.PROTECT)
    post_timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    post = models.TextField(max_length=8000)
    deleted = models.BooleanField(default=False) # just in case we need userdata

    def __str__(self) -> str:
        return f"{self.author} - {self.post_timestamp}"


class Emotion(models.Model):

    class EmotionChoices:
        LIKE = 1
        CHOICES = [
            (LIKE, 'Like'),
        ]

    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    user = models.ForeignKey(user_model, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    emotion = models.IntegerField(choices=EmotionChoices.CHOICES)

    class Meta:

        # make sure user-emotion-post is unique
        constraints = [
            models.UniqueConstraint(fields=['post', 'user', 'emotion'], 
                                    name='unique_emotion'),
        ]

    def __str__(self) -> str:
        return {}