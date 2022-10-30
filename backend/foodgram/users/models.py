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
        unique=True
    )
    first_name = models.CharField(
        max_length=200
    )
    last_name = models.CharField(
        max_length=200
    )
    email = models.EmailField(
        max_length=255,
        blank=False,
        null=False,
        unique=True
    )
    role = models.CharField(
        max_length=50,
        null=True,
        choices=ROLES,
        default=USER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ('id',)


class Follow(models.Model):
    """
    Модель подписки.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow',
            ),
        )
