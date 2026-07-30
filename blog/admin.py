from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = ("title", "author", "category", "created_at", "updated_at")
    list_filter = ("category", "created_at", "author")
    search_fields = ("title", "content", "author__username")
    readonly_fields = ("created_at", "updated_at")

    raw_id_fields = ("author",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = ("post", "author", "content_short", "created_at")
    list_filter = ("created_at", "author")
    search_fields = ("content", "post__title", "author__username")
    readonly_fields = ("created_at",)
    raw_id_fields = ("post", "author")

    def content_short(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_short.short_description = "Текст (сокращенно)"
