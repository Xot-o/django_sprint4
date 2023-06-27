from django.contrib import admin

from .models import Category, Location, Post, Comment


class PostAdmin(admin.ModelAdmin):
    """Основные параметры админки отвечающие за раздел с постами."""
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
        'category',
        'pub_date',
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)
    fitlter_horizontal = ('location',)


class PostInline(admin.TabularInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    """Раздел админки отвечающий за раздел категории."""
    inlines = (PostInline,)
    list_display = ('posts',)


class LocationAdmin(admin.ModelAdmin):
    """Раздел админки отвечающий за раздел местоположения."""
    inlines = (PostInline,)
    list_display = ('name',)


class CommentAdmin(admin.ModelAdmin):
    """Раздел админки отвечающий за радел комментариев."""
    list_display = (
        'text',
        'author',
        'post'
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
