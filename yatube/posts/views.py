from django.shortcuts import render, get_object_or_404
from .models import Post, Group

POSTS_VALUES = 10


def index(request):
    posts = Post.objects.all()[:POSTS_VALUES]
    title = 'Последние обновления на сайте'
    context = {
        'posts': posts,
        'title': title,

    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {slug}'
    posts = group.posts.all()[:POSTS_VALUES]
    context = {
        'group': group,
        'posts': posts,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)
