import random

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Comment, Genre, Review, Title, User

REVIEW_COUNT_ERROR = 'Можно оставить только один отзыв на произведение!'


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации  с генерацией кода подтверждения."""

    class Meta:
        model = User
        fields = (
            'email',
            'username'
        )

    def gen_code(self):
        return str(random.randrange(100000, 999999))


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки токенов аутентификации."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code',
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class MeSerializer(UserSerializer):
    """Сериализатор для текущего пользователя."""

    role = serializers.CharField(read_only=True)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели категории с полями имени и slug'а."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели жанра с полями имени и slug'а."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class GetTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели произведений при GET-запросах."""

    genre = GenreSerializer(
        many=True,
        read_only=True
    )
    category = CategorySerializer(
        read_only=True
    )
    rating = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели произведения."""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, title):
        serializer = GetTitleSerializer(title)
        return serializer.data


class ReviewSerialiser(serializers.ModelSerializer):
    """Сериализатор для модели отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        exclude = ('title',)

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST':
            title_id = self.context['view'].kwargs['title_id']
            if Review.objects.filter(
                title=get_object_or_404(Title, pk=title_id),
                author=request.user
            ).exists():
                raise ValidationError(REVIEW_COUNT_ERROR)
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        exclude = ('review',)
