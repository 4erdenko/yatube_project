from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, User

TEMP_NUMB_FIRST_PAGE = 10
TEMP_NUMB_SECOND_PAGE = 3


class PostPagesTests(TestCase):
    """Создаем базовый класс тестирования."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_author = Client()
        cls.user = User.objects.create_user(username="TestUser")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostPagesTests.user,
            group=PostPagesTests.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html/',
            reverse('posts:post_create'): 'posts/create_post.html/',
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, reverse_name)

    def test_index_show_correct_context(self):
        """Список постов в шаблоне index равен ожидаемому контексту."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_object = response.context['page_obj'][0]
        self.assertEqual(post_object.text, self.post.text)
        self.assertEqual(post_object.pub_date, self.post.pub_date)
        self.assertEqual(post_object.author, self.user)
        self.assertEqual(post_object.group, self.group)

    def test_group_list_show_correct_context(self):
        """Список постов в шаблоне group_list равен ожидаемому контексту."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(
            response.context.get('group').title, 'Тестовая группа'
        )
        self.assertEqual(self.post.text, 'Тестовый пост')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.group, self.group)
        self.assertEqual(response.context.get('group').slug, 'test-slug')
        self.assertEqual(response.context.get('group').description,
                         'Тестовое описание')

    def test_profile_show_correct_context(self):
        """Список постов в шаблоне profile равен ожидаемому контексту."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        post_object = response.context['page_obj'][0]
        self.assertIn('author', response.context)
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(post_object.text, self.post.text)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post_context = response.context.get('post')
        self.assertEqual(post_context.text, self.post.text)
        self.assertEqual(post_context.author, self.post.author)
        self.assertEqual(post_context.group, self.post.group)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edi и post_create сформирован с правильным
        контекстом."""
        url_names = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        for url_name in url_names:
            with self.subTest():
                response = self.authorized_client.get(url_name)
                self.assertIn('is_edit', response.context)
                if url_name == 'posts:post_edit':
                    self.assertIs(response.context['is_edit'], True)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)
                self.assertTrue('is_edit', response.context)

    def test_check_group_not_in_mistake_group_list_page(self):
        """Проверяем чтобы созданный Пост с группой не попал в чужую группу."""
        pages_num = 0
        group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-22',
            description='Тестовое описание 2'
        )
        Post.objects.create(group=self.group, author=self.user)
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': group_2.slug}))
        self.assertEqual(response.context['page_obj'].paginator.count,
                         pages_num)

    def test_paginator(self):
        """Проверяем работу страниц."""

        Post.objects.bulk_create(
            Post(
                text=f'Текст {index}',
                author=self.user,
                group=self.group
            ) for index in range(1, TEMP_NUMB_FIRST_PAGE +
                                 TEMP_NUMB_SECOND_PAGE))
        pages = (
            (1, TEMP_NUMB_FIRST_PAGE),
            (2, TEMP_NUMB_SECOND_PAGE)
        )
        url_name = (
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.user.username}),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})

        )
        for url in url_name:
            for page, count in pages:
                with self.subTest(url=url, page=page):
                    response = self.client.get(url, {'page': page})
                    self.assertEqual(len(response.context['page_obj']), count)
