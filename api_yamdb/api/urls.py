from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import SignupView, JWTokenView, UserViewSet
from .views import CategoryViewSet, CommentViewSet, GenreViewSet, ReviewViewSet, TitleViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='User')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
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
