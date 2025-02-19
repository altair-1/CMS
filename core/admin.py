from django.contrib import admin
from .models import User, Category, Content, Comment

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at')
    list_filter = ('is_published', 'categories')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    actions = ['publish_contents']

    def publish_contents(self, request, queryset):
        queryset.update(is_published=True, published_at=timezone.now())
    publish_contents.short_description = "Publish selected contents"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"