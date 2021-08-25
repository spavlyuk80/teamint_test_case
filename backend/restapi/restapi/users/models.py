from django.contrib.auth.models import User
from django.db import models

__all__ = ['Profile']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    # TODO add social data
    enriched = models.BooleanField(default=False)
    extra_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
