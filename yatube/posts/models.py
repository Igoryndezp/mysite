from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Max

User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Имя')
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name='О себе')
    profile_photo = models.ImageField(
        null=True,
        blank=True,
        upload_to="images/profile/",
        verbose_name='Фото')
    instagram = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Ссылка на Telegram')
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='День рождения')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Group(models.Model):
    title = models.CharField(
        max_length=200, verbose_name='Названиe группы',
        help_text='Группа, к которой будет относиться пост'
    )
    slug = models.SlugField(unique=True, verbose_name='Ссылка на группу')
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to="img_post/%Y/%m/%d",
        verbose_name='Фото')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    likes = models.ManyToManyField(
        User,
        blank=True,
        related_name='likes')
    dislikes = models.ManyToManyField(
        User,
        blank=True,
        related_name='dislikes')

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_author',
        verbose_name='Автор',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария')
    text = models.TextField(verbose_name='Комментарий')
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True, verbose_name='Статус')

    class Meta:
        ordering = ('created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Message(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='from_user'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='to_user'
    )
    body = models.TextField(max_length=1000, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def send_message(from_user, to_user, body):
        sender_message = Message(
            user=from_user,
            sender=from_user,
            recipient=to_user,
            body=body,
            is_read=True)
        sender_message.save()

        recipient_message = Message(
            user=to_user,
            sender=from_user,
            body=body,
            recipient=from_user,)
        recipient_message.save()
        return sender_message

    def get_messages(user):
        messages = (
            Message
            .objects.filter(user=user)
            .values('recipient')
            .annotate(last=Max('date'))
            .order_by('-last')
        )
        users = []
        for message in messages:
            users.append({
                'user': User.objects.get(pk=message['recipient']),
                'last': message['last'],
                'unread': Message.objects.filter(
                    user=user,
                    recipient__pk=message['recipient'],
                    is_read=False).count()
            })
        return users
