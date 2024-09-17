from django.db import models
from django.contrib.auth.models import AbstractUser

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLES = [
    (USER, 'пользователь'),
    (MODERATOR, 'модератор'),
    (ADMIN, 'администратор'),
]


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
