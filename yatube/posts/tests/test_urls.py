from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_status_allpage(self):
        """Проверка доступности адресов """
        url_status = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/auth/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            '/posts/1/edit/': HTTPStatus.FOUND,
        }
        for field, expected_value in url_status.items():
            with self.subTest(field=field):
                self.assertEqual(self.guest_client.get(field).status_code,
                                 expected_value
                                 )

    def test__url_template_guest_client(self):
        """Проверка шаблона для неавторизованного пользователя."""
        url_template = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for field, expected_value in url_template.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(self.guest_client.get(field),
                                        expected_value
                                        )

    def test__url_template_authorized_client(self):
        """Проверка шаблона для авторизованного пользователя."""
        url_template = {
            '/create/': 'forms/comment_form.html',
            '/posts/1/edit/': 'forms/comment_form.html',
        }
        for field, expected_value in url_template.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(self.authorized_client.get(field),
                                        expected_value
                                        )
