from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from posts.models import Emotion, Post
from posts.serializers import PostSerializer
from rest_framework.response import Response

class CreatePostView(CreateAPIView):
    # model = Post
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def perform_create(self, data, *args, **kwargs):
        data.save(author=self.request.user)
    
    def post(self,request, *args, **kwargs):
        _ = super().post(request, *args, **kwargs)
        return Response({'success':True}, status=status.HTTP_201_CREATED)


class LikePost(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmotionSerializer

    def perform_create(self, data, *args, **kwargs):
        """
        Make sure that this post-user-emotion is either 0-1
        and is unique
        """