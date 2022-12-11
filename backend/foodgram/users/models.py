from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя.
    """
    ADMIN = 'admin'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (USER, 'USER'),
    ]
    username = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        unique=True,
        verbose_name='Никнейм'
    )
    first_name = models.CharField(
        max_length=200,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=200,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        max_length=255,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Почта'
    )
    role = models.CharField(
        max_length=50,
        null=True,
        choices=ROLES,
        default=USER,
        verbose_name='Пользовательская роль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    """
    Модель подписки.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow',
            ),
        )
