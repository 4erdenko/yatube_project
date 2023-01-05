import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from ..forms import PostForm
from ..models import Post, Group, User, Comment, Follow

TEMP_NUMB_FIRST_PAGE = 10
TEMP_NUMB_SECOND_PAGE = 3

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    """Создаем базовый класс тестирования."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_author = Client()
        cls.user = User.objects.create_user(username="TestUser")
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostPagesTests.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
            image=PostPagesTests.uploaded,
        )
        cls.comment = Comment.objects.create(
            text='Комментарий',
            author=PostPagesTests.user,
            post=PostPagesTests.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
        self.assertEqual(post_object.image, self.post.image)

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
        self.assertEqual(self.post.image, self.post.image)
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
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.group, self.group)
        self.assertEqual(post_object.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post_context = response.context.get('post')
        self.assertEqual(post_context.text, self.post.text)
        self.assertEqual(post_context.author, self.post.author)
        self.assertEqual(post_context.group, self.post.group)
        self.assertEqual(post_context.image, self.post.image)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit и post_create сформирован с правильным
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
                elif url_name == 'posts:post_create':
                    self.assertIs(response.context['is_edit'], False)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)

    def test_check_group_not_in_mistake_group_list_page(self):
        """Проверяем чтобы созданный Пост с группой не попал в чужую группу."""
        pages_num = 0
        group_new = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-22',
            description='Тестовое описание 2'
        )
        Post.objects.create(group=self.group, author=self.user)
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': group_new.slug}))
        self.assertEqual(response.context['page_obj'].paginator.count,
                         pages_num)

    def test_paginator(self):
        """Проверяем работу страниц."""

        Post.objects.bulk_create(
            Post(
                text=f'Текст {index}',
                author=self.user,
                group=self.group
            ) for index in range(1, TEMP_NUMB_FIRST_PAGE
                                 + TEMP_NUMB_SECOND_PAGE))
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

    def cache_test(self):
        """Проверяем работу кэша."""
        post = Post.objects.create(
            text='Кэш тест',
            author=self.user
        )
        content_add = self.authorized_client.get(
            reverse('posts:index')).content
        post.delete()
        content_delete = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_cache_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_add, content_cache_clear)


class FollowViewsTest(TestCase):
    def setUp(self):
        self.follower = User.objects.create_user(username='Follower')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower)
        self.author = User.objects.create_user(username='author')
        self.post_author = Post.objects.create(
            text='текст автора',
            author=self.author,
        )

    def test_follow_author(self):
        follow_count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', args={self.author}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        last_follow = Follow.objects.latest('id')
        self.assertEqual(last_follow.author, self.author)
        self.assertEqual(last_follow.user, self.follower)
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.author}))

    def test_unfollow_author(self):
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', args={self.author}))
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', args={self.author}))
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.author}))
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_new_post_follow(self):
        self.authorized_client.get(
            reverse('posts:profile_follow', args={self.author}))
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        post_follow = response.context['page_obj'][0]
        self.assertEqual(post_follow, self.post_author)

    def test_new_post_unfollow(self):
        new_author = User.objects.create_user(username='new_author')
        self.authorized_client.force_login(new_author)
        Post.objects.create(
            text='новый текст автора',
            author=new_author,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
