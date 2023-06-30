from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment


User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма для публикаций."""

    class Meta:
        model = Post
        exclude = ('author', 'comment_count')
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%d/%m/%Y %H:%M',
                attrs={'type': 'datetime-local'}
            ),
            'comment_count': forms.HiddenInput()
        }


class CommentForm(forms.ModelForm):
    """Форма для комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)


class ProfileForm(forms.ModelForm):
    """Форма для профиля."""

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email'
        )
