import datetime as dt

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.db.models import Count, Q
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm, ProfileForm


class ProfileLoginView(LoginView):
    def get_success_url(self):
        """Получение адреса."""
        url = reverse(
            'blog:profile',
            args=(self.request.user.get_username(),)
        )
        return url


def get_page_obj(paginator, page_number):
    """Получаем страницу с постами."""
    get_page_obj = paginator.get_page(page_number)
    return get_page_obj


@login_required
def edit_profile(request, username):
    """Изменение профиля пользователя."""
    user = get_object_or_404(User, username=username)
    if user.username != request.user.username:
        return redirect('login')
    form = ProfileForm(request.POST or None, instance=user)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, 'blog/user.html', context)


def profile_view(request, username):
    """Отображает профиль пользователя."""
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=profile_user
    ).order_by(
        '-pub_date'
    ).annotate(comment_count=Count('comment__post'))
    can_edit_profile = request.user == profile_user

    paginator = Paginator(posts, settings.PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = get_page_obj(paginator, page_number)

    post_images = [post.image for post in posts if post.image]

    context = {
        'profile': profile_user,
        'posts': posts,
        'can_edit_profile': can_edit_profile,
        'page_obj': page_obj,
        'post_images': post_images,
    }
    return render(request, 'blog/profile.html', context)


class PostListView(ListView):
    """Отображает посты на странице."""
    template_name = 'blog/index.html'
    model = Post
    queryset = Post.objects.filter(
        is_published=True,
        pub_date__lte=dt.datetime.now(),
        category__is_published=True
    ).select_related('author').annotate(comment_count=Count('comment__post'))
    ordering = '-pub_date'
    paginate_by = settings.PAGINATE_BY


def category_posts(request, category_slug):
    """Функция отвечает за вывод категории поста."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = category.posts.filter(
        pub_date__lte=dt.datetime.now(),
        is_published=True,
    )
    paginator = Paginator(post_list, settings.PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = get_page_obj(paginator, page_number)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


class DispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        """Отправляет изменения/удаления поста."""
        self.post_id = kwargs['pk']
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Проверка валидности формы."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Получение адреса."""
        url = reverse(
            'blog:profile',
            args=(self.request.user.get_username(),)
        )
        return url


class PostUpdateView(LoginRequiredMixin, DispatchMixin, UpdateView):
    """Обновление поста."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[str(self.post_id)])


class PostDeleteView(LoginRequiredMixin, DispatchMixin, DeleteView):
    """Удаление поста."""
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'


class PostDetailView(DetailView):
    """Детализированное отображение поста."""
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        queryset = Post.objects.filter(
            Q(is_published=True) | Q(author=self.request.user)
        )
        return get_object_or_404(
            queryset,
            pk=self.kwargs.get('pk'),
        )

    def get_context_data(self, **kwargs):
        """Получение данных контекста."""
        context = super().get_context_data(**kwargs)

        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related(
                'author'
            )
        )
        
        return context


@login_required
def add_comment(request, pk):
    """Добавление комментария."""
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, comment_id, post_id):
    """Редактирование комментария."""
    instance = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if instance.author != request.user:
        return redirect('login')
    form = CommentForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'comment': instance
    }
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, comment_id, post_id):
    """Удаление комментария."""
    instance = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', pk=post_id)
    context = {'comment': instance}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)
