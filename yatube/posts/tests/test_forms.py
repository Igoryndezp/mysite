from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from posts.forms import PostForm
from posts.models import Post

User = get_user_model()

class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        #cls.image1 = "/yatube/media/img_post/logo.png"
        #cls.a= Image.new(mode="RGB", size=(200, 200))

    def test_create_post(self):
        """Проверка формы создания поста."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': 'StasBasov'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Проверка формы редактирования поста."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост1',
        )
        post_count = Post.objects.count()
        form_data_edit = {
            'text': 'edit post',
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data_edit,
            follow=True
        )
        self.assertRedirects(response_edit, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text='edit post',
            ).exists()
        )
