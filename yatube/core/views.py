from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'core/404.html',
                  {'exception': exception}, status=404)


def permission_denied(request, reason=''):
    return render(request, 'core/403.html',
                  {'reason': reason}, status=403)
