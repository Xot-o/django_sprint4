from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class BaseModelForm(models.Model):
    """Абстрактная модель,
    добавляет флаг is_published(опубликован ли пост),
    и время создания поста created_at.
    """
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, '
        'чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class Category(BaseModelForm):
    """Класс отвечающий за категории постов."""
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, '
        'цифры, дефис и подчёркивание.',
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModelForm):
    """Класс отвечающий за местоположения в постах."""
    name = models.CharField('Название места', max_length=256, unique=True)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModelForm):
    """Основной класс , отвечающий за пост , и всю информацию в нем."""
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    comment_count = models.IntegerField(
        'Количество комментариев',
        default=0)
    image = models.ImageField('Фото', blank=True)
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        default=timezone.now(),
        help_text='Если установить дату '
                  'и время в будущем — можно'
                  ' делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='posts',
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='posts',
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to="images/profile/"
    )

    def __str__(self):
        return str(self.user)


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Заголовок поста',
        related_name='comment',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text
