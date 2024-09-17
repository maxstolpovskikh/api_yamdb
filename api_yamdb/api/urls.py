from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


auth_patterns = [
    path('signup/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/', TokenRefreshView.as_view(), name='token_refresh'),
]

v1_patterns = [
    path('auth/', include(auth_patterns)),
]

urlpatterns = [
    path('v1/', include(v1_patterns)),
]