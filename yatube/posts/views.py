from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group

User = get_user_model()


def paginate_page(queryset, request):
    paginator = Paginator(queryset, settings.POSTS_VALUES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.select_related('author', 'group')
    title = 'Последние обновления на сайте'
    context = {
        'title': title,
        'posts': posts,
        'page_obj': paginate_page(posts, request),
    }
    return render(request, 'posts/index.html', context)


# @login_required
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {slug}'
    posts = group.posts.select_related('author', 'group')
    context = {
        'group': group,
        'title': title,
        'page_obj': paginate_page(posts, request),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author', 'group')
    context = {
        'author': author,
        'page_obj': paginate_page(posts, request),

    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    context = {
        'post': post,

    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    context = {
        'form': form,
        'is_edit': False,
    }
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', username=form.author)
    return render(request, 'posts/create_post.html/', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post.pk)
    if form.is_valid() and request.method == 'POST':
        form.save()
        return redirect('posts:post_detail', post.pk)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/create_post.html/', context)
