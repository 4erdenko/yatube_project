import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, User, Comment

AUTHOR_USERNAME = 'TestAuthor'
POST_TEXT = 'Тестовый текст'
GROUP_TITLE = 'Тестовая группа'
SLUG = 'SlugTest'
GROUP_DESCRIPTION = 'Тестовое описание'
SECOND_GROUP_TITLE = 'Вторая тестовая группа'
SECOND_SLUG = 'test_group'
SECOND_GROUP_DESCRIPTION = 'Тестовое описание второй группы'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=SLUG,
            description=GROUP_DESCRIPTION
        )
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
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.form_comment_data = {
            'text': 'Комментарий',
            'author': 'Author',
        }
        cls.post = Post.objects.create(
            author=cls.auth_user,
            text=POST_TEXT,
            group=cls.group,
            image=None,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth_user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        form_data = {'text': 'Тестовый текст',
                     'group': self.group.id,
                     'image': self.uploaded,
                     }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.auth_user}))
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.auth_user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, 'posts/small.gif')
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        uploaded_edit = SimpleUploadedFile(
            name='small1.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        second_group = Group.objects.create(
            title=SECOND_GROUP_TITLE,
            slug=SECOND_SLUG,
            description=SECOND_GROUP_DESCRIPTION,
        )

        form_data = {
            'text': 'Изменяем текст',
            'group': second_group.id,
            'image': uploaded_edit
        }
        post_edit_url = reverse('posts:post_edit', args=[self.post.id])
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        edited_post = self.authorized_client.get(
            post_edit_url).context['post']
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group, second_group)
        self.assertEqual(edited_post.image, 'posts/small1.gif')
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_not_create_guest_client(self):
        """Валидная форма создания поста если юзер не авторизован."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Новый текст', 'group': 'Новая группа для '
                                                     'поста'}
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_user_cant_comment_post(self):
        """Неавторизованный юзер не может оставить комментарий."""
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.pk
            }),
            data=self.form_comment_data,
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
        self.assertEqual(Comment.objects.count(), 0)

    def test_auth_user_can_comment_post(self):
        """Авторизованный юзер может оставить комментарий."""
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.pk
            }),
            data=self.form_comment_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.pk
        }))
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(
            response.context['post'].comments.all()[0].text,
            self.form_comment_data['text']
        )
