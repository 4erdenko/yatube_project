from django.test import TestCase

from ..models import Group, Post, User

TEXT_MAX = 15
FIELD_VERBOSE = {'text': 'Текст',
                 'group': 'Группа', }
FIELD_HELP_TEXTS = {'text': 'Напишите свой текст',
                    'group': 'Выберите группу', }


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 12',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает str."""
        self.assertEqual(self.post.text[:TEXT_MAX], str(self.post))
        self.assertEqual(self.group.title, str(self.group))

    def test_help_text_name(self):
        """help_text полей text и group совпадает с ожидаемым"""
        for value, expected in FIELD_HELP_TEXTS.items():
            with self.subTest(value=value):
                self.assertEqual(Post._meta.get_field(value).help_text,
                                 expected)

    def test_verbose_name(self):
        """verbose_name полей text и group совпадает с ожидаемым"""
        for value, expected in FIELD_VERBOSE.items():
            with self.subTest(expected=expected):
                self.assertEqual(Post._meta.get_field(value).verbose_name,
                                 expected)
