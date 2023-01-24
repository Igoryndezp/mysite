from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост тестовый пост тестовый пост тестовый пост',
        )

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        name = group.title
        self.assertEqual(name, str(group))

    def test_models_have_correct_object_names_post(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        name = post.text
        self.assertEqual(name[:15], str(post))

    def test_title_label(self):
        """verbose_name поля title совпадает с ожидаемым."""
        group = PostModelTest.group
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'Названиe группы')

    def test_title_help_text(self):
        """help_text поля title совпадает с ожидаемым."""
        group = PostModelTest.group
        help_text = group._meta.get_field('title').help_text
        self.assertEqual(help_text, 'Группа, к которой будет относиться пост')
