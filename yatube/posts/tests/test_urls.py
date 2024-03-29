from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=cls.group
        )
        cls.templates = [
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.user}/',
            f'/posts/{cls.post.id}/',
        ]
        cls.templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html/',
            '/create/': 'posts/create_post.html/',
        }
        cls.create_edit_template = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{cls.post.id}/edit/':
                f'/auth/login/?next=/posts/{cls.post.id}/edit/',
        }

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_urls_exists_at_desired_location(self):
        for address in self.templates:
            with self.subTest(address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_and_edit(self):
        """Проверка создания поста юзером."""
        url_names = {
            '/create/': 'posts/create_post.html/',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html/',
        }
        for url_name in url_names:
            with self.subTest(url_name):
                response = self.authorized_client.get(url_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous_on_auth_login(self):
        """Страница create/edit доступна авторизованному пользователю."""

        for url, expected in self.create_edit_template.items():
            with self.subTest(expected=expected):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, expected)

    def test_unexisting_page_at_desired_location(self):
        """Страница /unexisting_page/ должна выдать ошибку."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_non_author_cannot_edit_post(self):
        """Создаем юзера не автора, авторизуем его и пытаемся изменить пост"""
        user = User.objects.create(username='NotAuthor')
        not_author_client = Client()
        not_author_client.force_login(user)
        response = not_author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_custom_404(self):
        """Проверка на кастомную страницу 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
