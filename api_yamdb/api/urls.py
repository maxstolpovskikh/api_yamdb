from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SignupView, JWTokenView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='User')

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
