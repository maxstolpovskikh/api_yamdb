import random

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import IsAuthenticatedAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTitleSerializer,
                          ReviewSerialiser, SignUpSerializer, TitleSerializer,
                          TokenSerializer, UserSerializer, MeSerializer)


class SignupView(APIView):
    permission_classes = (permissions.AllowAny,)

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

        return Response(
            {'email': user.email, 'username': user.username},
            status=status.HTTP_200_OK
        )


class JWTokenView(APIView):
    permission_classes = (permissions.AllowAny,)

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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    filterset_fields = ('username')
    search_fields = ('username', )
    lookup_field = 'username'

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated, )
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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerialiser

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])
