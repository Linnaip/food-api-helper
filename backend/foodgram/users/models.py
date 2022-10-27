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
        (USER, 'User'),
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

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=['username', 'email'],
                                    name='uniq_signup')
        )
