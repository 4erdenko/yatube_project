from django.shortcuts import render, get_object_or_404
from .models import Post, Group
# Create your views here.


# Главная страница
def index(request):
    # Одна строка вместо тысячи слов на SQL:
    # в переменную posts будет сохранена выборка из 10 объектов модели Post,
    # отсортированных по полю pub_date по убыванию (от больших значений к меньшим)
    posts = Post.objects.order_by('-pub_date')[:10]
    # В словаре context отправляем информацию в шаблон
    title = 'Последние обновления на сайте'
    context = {
        'posts': posts,
        'title': title,

    }
    return render(request, 'posts/index.html', context)


# Страница с группами
#def group_posts(request, slug):
#    template = 'posts/group_posts.html'
#    title = 'Группы'
#    context = {
#        'title': title,
#        'text': 'Здесь будет информация о группах проекта Yatube'
#    }
#    return render(request, template,context, slug)
def group_posts(request, slug):
    # Функция get_object_or_404 получает по заданным критериям объект
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # В нашем случае в переменную group будут переданы объекты модели Group,
    # поле slug у которых соответствует значению slug в запросе
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {slug}'
    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'group': group,
        'posts': posts,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)


# Страница с постами в группах
#def group_list(request):
#    template = 'posts/group_list.html'
#    title = 'Лев Толстой'
#    context = {
#        'title': title,
#       'text':'Лёва Толстой'
#    }
#    return render(request, template, context)
