from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    DJSUPERUSER = 'djadmin'
    ROLES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
        (DJSUPERUSER, 'djsuperuser'),
    )
    bio = models.TextField(
        max_length=500, blank=True, null=True,
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=30, choices=ROLES,
        default='user', verbose_name='Роль'
    )
    confirmation_code = models.CharField(
        max_length=200, default='0000',
        verbose_name='Проверочный код'
    )


class Review(models.Model):
    # title = models.ForeignKey(
        # Title,
        # on_delete=models.CASCADE,
        # related_name='reviews',
        # verbose_name='Произведение'
    # )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор ревью'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(10)],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Ревью'
        verbose_name_plural = 'Ревьюшечки'

    def __str__(self):
        return f'{self.title}, {self.score}, {self.author}'
