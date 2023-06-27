from django.shortcuts import render

from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Раздел о проекте."""
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Раздел сайта с правилами."""
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Ошибка: страница не найдена."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Ошибка csrf токена."""
    return render(request, 'pages/403csrf.html', status=403)


def internal_server_error(request, reason=''):
    """Внутренняя ошибка сервера."""
    return render(request, 'pages/500.html', status=500)
