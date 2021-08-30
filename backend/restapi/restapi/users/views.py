from django.contrib.auth.models import User

# Create your views here.
from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from .serializers import UserSerializer

__all__ = ['CreateUserView']


class CreateUserView(CreateAPIView):
    model = User
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
