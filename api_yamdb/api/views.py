from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import IsAdmin, IsAuthorOrAdminOrModerOrReadOnly, ReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTitleSerializer, MeSerializer,
                          ReviewSerialiser, SignUpSerializer, TitleSerializer,
                          TokenSerializer, UserSerializer)

ALLOWED_METHODS = ['get', 'post', 'patch', 'delete']


class SignupView(APIView):
    """Представление для регистрации и отправки кода подтверждения."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if not serializer.is_valid():
            email = serializer.initial_data.get('email')
            username = serializer.initial_data.get('username')
            user = User.objects.filter(email=email).first()
            if user and user.username == username:
                user.confirmation_code = serializer.generate_confirmation_code()
                user.save()
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            user = serializer.save()

        send_mail(
            'Регистрация в Yamdb',
            f'Код подтверждения {user.confirmation_code}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class JWTokenView(APIView):
    """Представление для получения JWT токена по коду подтверждения."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if data.get('confirmation_code') == user.confirmation_code:
            return Response(
                {'token': str(RefreshToken.for_user(user).access_token)},
                status=status.HTTP_201_CREATED
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями с дополнительным методом 'me'."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    filterset_fields = ('username')
    lookup_field = 'username'
    http_method_names = ALLOWED_METHODS

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = MeSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(ListCreateDestroyViewSet):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin | ReadOnly]


class GenreViewSet(ListCreateDestroyViewSet):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdmin | ReadOnly]


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений."""

    queryset = (
        Title.objects
        .annotate(
            rating=Avg('reviews__score')
        )
        .order_by('reviews__score')
    )
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ALLOWED_METHODS
    permission_classes = [IsAdmin | ReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""
 
    serializer_class = ReviewSerialiser
    http_method_names = ALLOWED_METHODS
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrAdminOrModerOrReadOnly
    ]

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""

    serializer_class = CommentSerializer
    http_method_names = ALLOWED_METHODS
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrAdminOrModerOrReadOnly
    ]

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])
