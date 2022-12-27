from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User

AUTHOR_USERNAME = 'TestAuthor'
POST_TEXT = 'Тестовый текст'
GROUP_TITLE = 'Тестовая группа'
SLUG = 'SlugTest'
GROUP_DESCRIPTION = 'Тестовое описание'
SECOND_GROUP_TITLE = 'Вторая тестовая группа'
SECOND_SLUG = 'test_group'
SECOND_GROUP_DESCRIPTION = 'Тестовое описание второй группы'


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            id=1,
            title=GROUP_TITLE,
            slug=SLUG,
            description=GROUP_DESCRIPTION
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth_user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        form_data = {'text': 'Тестовый текст',
                     'group': self.group.id,
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
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        second_group = Group.objects.create(
            title=SECOND_GROUP_TITLE,
            slug=SECOND_SLUG,
            description=SECOND_GROUP_DESCRIPTION,
        )
        post = Post.objects.create(
            author=self.auth_user,
            text=POST_TEXT,
            group=self.group,
        )
        form_data = {'text': 'Изменяем текст', 'group': second_group.id}
        post_edit_url = reverse('posts:post_edit', args=[post.id])
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=({post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        edited_post = self.authorized_client.get(
            post_edit_url).context['post']
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group, second_group)
        self.assertEqual(Post.objects.count(), +1)
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
        self.assertRedirects(response,
                             f'/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
