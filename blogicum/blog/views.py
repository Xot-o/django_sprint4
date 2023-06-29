from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
import datetime as dt
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm, ProfileForm


class ProfileLoginView(LoginView):
    def get_success_url(self):
        url = reverse(
            'blog:profile',
            args=(self.request.user.get_username(),)
        )
        return url


@login_required
def edit_profile(request, username):
    '''Изменение профиля пользователя.'''
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
    posts = Post.objects.filter(author=profile_user).order_by('-pub_date')
    can_edit_profile = request.user == profile_user

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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
    template_name = 'blog/index.html'
    current_time = dt.datetime.now()
    model = Post
    queryset = Post.objects.filter(
        is_published=True,
        pub_date__lte=current_time,
        category__is_published=True
    ).select_related('author')
    ordering = '-pub_date'
    paginate_by = 10


def category_posts(request, category_slug):
    """Функция отвечает за вывод категории поста."""
    current_time = dt.datetime.now()
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = category.posts.filter(
        pub_date__lte=current_time,
        is_published=True,
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Проверка валидности формы."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.is_authenticated:
            url = reverse(
                'blog:profile',
                args=(self.request.user.get_username(),)
            )
        else:
            url = reverse('login')
        return url


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_id = kwargs['pk']
        instance = get_object_or_404(Post, pk=self.post_id)
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=self.post_id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = reverse('blog:post_detail', args=[str(self.post_id)])
        return url


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
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
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        post.comment_count += 1
        post.save()
    return redirect('blog:post_detail', pk=pk)

@login_required
def edit_comment(request, comment_id, post_id):
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
    instance = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    post = get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect('login')
    context = {'comment': instance}
    if request.method == 'POST':
        instance.delete()
        post.comment_count -= 1
        post.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)
