from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet, JWTokenView,
                    ReviewViewSet, SignupView, TitleViewSet, UserViewSet)


router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(r'users', UserViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

auth_patterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', JWTokenView.as_view(), name='token'),
]

v1_patterns = [
    path('auth/', include(auth_patterns)),
    path('', include(router.urls)),
]

urlpatterns = [
    path('v1/', include(v1_patterns)),
]
