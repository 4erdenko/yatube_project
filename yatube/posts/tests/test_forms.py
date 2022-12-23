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
            title=GROUP_TITLE,
            slug=SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.second_group = Group.objects.create(
            title=SECOND_GROUP_TITLE,
            slug=SECOND_SLUG,
            description=SECOND_GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.auth_user,
            text=POST_TEXT,
            group=cls.group,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

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
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.auth_user.
                    username})
        )
        post = Post.objects.all()[0]
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.auth_user)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(Post.objects.count(), +2)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        form_data = {'text': 'Изменяем текст', 'group': self.second_group.id}
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
            self.POST_DETAIL_URL).context['post']
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])
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
