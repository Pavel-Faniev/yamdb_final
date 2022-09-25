from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

USER_ROLE = 'user'
MODER_ROLE = 'moderator'
ADMIN_ROLE = 'admin'
SUPER_ROLE = 'superuser'

USER_ROLES = [
    (USER_ROLE, 'user'),
    (MODER_ROLE, 'moderator'),
    (ADMIN_ROLE, 'admin'),
    (SUPER_ROLE, 'superuser'),
]


# Create new User Model
class User(AbstractUser):
    bio = models.TextField(
        verbose_name='Биография',
        help_text='Информация о пользователе',
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=25,
        choices=USER_ROLES,
        verbose_name='Роль',
        help_text='Роль пользователя',
        default=USER_ROLE,  # по умолчанию просто пользователь
        blank=False,
        null=False,
    )
    confirmation_code = models.CharField(
        max_length=36,
        # это нужно, чтобы из под админа потом можно было нормально зайти
        default='123456',
    )

    @property
    def is_admin(self):
        # checks if user is admin
        if self.role == ADMIN_ROLE or self.is_staff:
            return True
        return False

    @property
    def is_moderator(self):
        # checks if user is moderator
        if self.role == MODER_ROLE:
            return True
        return False

    @property
    def is_super(self):
        # checks if user is superuser
        if self.role == SUPER_ROLE:
            return True
        return False


class Category(models.Model):
    """Модель категорий произведений."""
    name = models.CharField(max_length=256, verbose_name="Категория")
    slug = models.SlugField(max_length=50,
                            unique=True)

    class Meta:
        verbose_name_plural = "Категории"
        verbose_name = "Категория"
        indexes = [
            models.Index(fields=['slug'])
        ]

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанра произведений."""
    name = models.CharField(max_length=256, verbose_name="Жанр")
    slug = models.SlugField(
        max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Жанры"
        verbose_name = "Жанр"
        indexes = [
            models.Index(fields=['slug'])
        ]

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений."""
    name = models.CharField(max_length=256,
                            verbose_name="Название произведения")
    year = models.IntegerField(verbose_name="Год создания произведения")
    description = models.TextField(verbose_name="Описание произведения")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 related_name="titles",
                                 verbose_name="Категория_произведения",
                                 )
    genre = models.ManyToManyField(Genre, related_name="titles", blank=True)

    class Meta:
        verbose_name_plural = "Произведения"
        verbose_name = "Произведение"

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзывов о произведении."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    text = models.TextField(
        max_length=256,
        verbose_name='Отзыв',
        help_text='Оставьте отзыв',
        blank=True,
        null=True
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        verbose_name='Рейтинг',
        help_text='Поставьте оценку'
    )
    pub_date = models.DateTimeField(
        'Дата публикации отзыва',
        auto_now_add=True
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]


class Comment(models.Model):
    """Модель комментариев."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField(
        max_length=256,
        verbose_name='Комментарий',
        help_text='Оставьте комментарий',
        blank=False,
        null=False
    )
    pub_date = models.DateTimeField(
        'Дата публикации комментария',
        auto_now_add=True
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
