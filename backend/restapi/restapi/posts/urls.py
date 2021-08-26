from django.urls import path
from .views import CreatePostView, LikePost


urlpatterns = [
    path('post/', CreatePostView.as_view(), name='post-create'),
    path('post/<int:pk>/like', LikePost.as_view(), name='like-post')
]