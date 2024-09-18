from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import regex_validator, validate_not_me


DESCRIPTION_LENGTH_LIMIT = 20

MIN_RATING = 1
MAX_RATING = 10
WRONG_RATING = (f'Оценка должна лежать в диапазоне от {MIN_RATING} '
                f'до {MAX_RATING}!')

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLES = [
    (USER, 'пользователь'),
    (MODERATOR, 'модератор'),
    (ADMIN, 'администратор'),
]


class User(AbstractUser):
    """Кастомный класс пользователей."""
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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Title(models.Model):
    pass


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
        auto_now_add=True
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
