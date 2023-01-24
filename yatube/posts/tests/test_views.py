from functools import cache

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        
        super().setUpClass()
        Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Текст'
        )
        cls.user = User.objects.create_user(username='StasBasov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Заголовок1',
            slug='test-slug1',
            description='Текст'
        )
        cls.image1 ="/yatube/media/img_post/logo.png"
        Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.image1
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'StasBasov'})
            ),
            'forms/comment_form.html': (
                reverse('posts:post_edit', kwargs={'post_id': '1'})
            ),

            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_task_list_page_authorized_uses_correct_template(self):
        """URL-адрес использует шаблон forms/comment_form.html."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'forms/comment_form.html')

    def test_index_paginator(self):
        """Проверка paginator для старицы index."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_group_list_paginator(self):
        """Проверка paginator для страцины группы."""
        response = self.authorized_client.get(
            (reverse('posts:group_list', kwargs={'slug': 'test-slug1'}))
        )
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_profile_paginator(self):
        """Проверка paginator для profile."""
        for i in range(9):
            Post.objects.create(
                author=self.user,
                text='Тестовый пост',
                group=self.group
            )
        response = self.authorized_client.get(
            (reverse('posts:profile', kwargs={'username': 'StasBasov'}))
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_paginator_second_page(self):
        """Проверка второй страницы paginator для profile."""
        response = self.authorized_client.get(
            (reverse('posts:profile', kwargs={'username': 'StasBasov'})
             + '?page=2')
        )
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        index_title_0 = first_object.author
        index_text_0 = first_object.text
        index_slug_0 = first_object.group
        index_image_0 = first_object.image
        self.assertEqual(index_title_0, self.user)
        self.assertEqual(index_text_0, 'Тестовый пост')
        self.assertEqual(index_slug_0, self.group)
        self.assertEqual(index_image_0, self.image1)


    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail', kwargs={'post_id': '1'})))
        self.assertEqual(response.context.get('post').author, self.user)
        self.assertEqual(response.context.get('post').text, 'Тестовый пост')
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(response.context.get('post').image, self.image1)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': 'test-slug1'}))
                    )
        self.assertEqual(response.context.get('group').title, 'Заголовок1')
        self.assertEqual(response.context.get('group').slug, 'test-slug1')
        self.assertEqual(response.context.get('group').description, 'Текст')

    #def test_index_pages_show_correct_context(self):
    #    """Шаблон index_pages сформирован с правильным контекстом."""
    #    response = (self.authorized_client.
    #                get(reverse('posts:index')))
    #    self.assertEqual(response.context.get('post').image, self.image1)            
    #    self.assertEqual(response.context.get('post').author, self.user)
    #    self.assertEqual(response.context.get('post').text, 'Тестовый пост')
    #    self.assertEqual(response.context.get('post').group, self.group)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile_pages сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                                kwargs={'username': 'StasBasov'}))
                    )
        self.assertEqual(response.context.get('post').author, self.user)
        self.assertEqual(response.context.get('post').text, 'Тестовый пост')
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(response.context.get('post').image, self.image1)


    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=self.user,
        )
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)