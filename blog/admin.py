from django.contrib import admin

from .models import Category, Comment, Post, Tag

# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "category",
        "status",
        "views_count",
        "created_at",
    ]
    list_filter = ["status", "category", "created_at"]
    search_fields = ["title", "body", "author__email"]
    prepopulated_fields = {"slug": ("title",)}
    list_select_related = ["author", "category"]
    list_editable = ["status"]
    readonly_fields = ["created_at", "updated_at", "views_count"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "post", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["author__email", "body"]
    list_editable = ["is_approved"]
    list_select_related = ["author", "post"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
