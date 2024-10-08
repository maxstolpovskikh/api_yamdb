from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import regex_validator, validate_not_me


DESCRIPTION_LENGTH_LIMIT = 20
MAX_CHAR_LENGTH = 250
MAX_SLUG_LENGTH = 50

MIN_RATING = 1
MAX_RATING = 10
WRONG_RATING = (f'Оценка должна лежать в диапазоне от {MIN_RATING} '
                f'до {MAX_RATING}!')


class User(AbstractUser):
    """Кастомный класс пользователей."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLES = [
        (USER, 'пользователь'),
        (MODERATOR, 'модератор'),
        (ADMIN, 'администратор'),
    ]

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        validators=[regex_validator, validate_not_me],
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=20,
        choices=ROLES,
        default=USER,
    )
    bio = models.TextField(
        'О себе',
        blank=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
    )
    confirmation_code = models.CharField(max_length=100, blank=True)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Category(models.Model):
    """Модель категории."""

    name = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        verbose_name='Hазвание категории',
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH,
        verbose_name='Идентификатор',
        unique=True,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH_LIMIT]


class Genre(models.Model):
    """Модель жанра."""

    name = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        verbose_name='Hазвание жанра',
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH,
        verbose_name='Идентификатор',
        unique=True,
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH_LIMIT]


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        verbose_name='Hазвание произведения',
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='год выхода',
        validators=[
            MinValueValidator(
                0,
                message='Год не может быть меньше нуля'
            ),
            MaxValueValidator(
                int(datetime.now().year),
                message='Год не может быть из будущего'
            )
        ],
        db_index=True
    )
    description = models.TextField(
        verbose_name='описание',
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='категория',
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH_LIMIT]


class GenreTitle(models.Model):
    """Промежуточная модель для связи между жанрами и произведениями."""

    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )

    class Meta:
        verbose_name = 'Жанр - произведение'
        verbose_name_plural = 'Жанры - произведения'
        ordering = ('id',)

    def __str__(self):
        return f'{self.title} соответствует жанру: {self.genre}'


class Review(models.Model):
    """Модель отзывов."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    text = models.TextField('Текст отзыва')
    score = models.PositiveIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(
                limit_value=MIN_RATING,
                message=WRONG_RATING,
            ),
            MaxValueValidator(
                limit_value=MAX_RATING,
                message=WRONG_RATING,
            )
        ]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        ordering = ('pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            ),
        ]

    def __str__(self):
        return (
            f'{self.title} | '
            f'{self.score} | '
            f'{self.text[:DESCRIPTION_LENGTH_LIMIT]} | '
            f'{self.author[:DESCRIPTION_LENGTH_LIMIT]}'
        )


class Comment(models.Model):
    """Модель комментариев."""

    text = models.TextField('Текст комментария')
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('pub_date',)

    def __str__(self):
        return (
            f'{self.text[:DESCRIPTION_LENGTH_LIMIT]} | '
            f'{self.review} | '
            f'{self.author} | '
        )
