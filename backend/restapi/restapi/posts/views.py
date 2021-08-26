from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
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
        return _


class LikePost(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        ]

    def post(self, request, *args, **kwargs):
        """
        Custom post request, that allows to like the post
        works in such a way that if post like already exists,
        it will remove the like.
        """
        post_pk = self.kwargs.get('pk')

        emotion, created = Emotion.objects.get_or_create(
            post__pk=post_pk, user__id=self.request.user.id,
            defaults={
                'post_id': post_pk,
                'user_id': self.request.user.id,
                'emotion': 1}
                )
        # if -1 or 0, will make emotion 1 (like)
        # if 1 will make emotion 0
        # TODO: will work only with like/dislike, if more emotions needed,
        # need to think about different logics
        if not created:
            emotion.emotion = 0 if emotion.emotion == 1 else 1
            emotion.save()

        return Response({'success':True})
