from typing import Type
import jwt
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

__all__ = ['Profile']

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('No username submitted')
        
        if email is None:
            raise TypeError('No email submitted')
        
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
    
    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Superuser must have a password')
        
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    @property
    def token(self):
        return self._generate_jwt_token()
    
    def get_full_name(self):
        return self.username

    def fet_short_name(self):
        return self.username

    def _generate_jwt_token(self):
        
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strfitem('%s')),

        }, settings.SECRET_KEYS, algorithm = 'HS256')

        return token.encode('urf-8')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    # TODO add social data

