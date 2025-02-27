from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, Category, Content, Comment
from django.utils import timezone

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'avatar')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at', 'created_at', 'updated_at')
    list_filter = ('is_published', 'categories', 'created_at', 'updated_at')
    search_fields = ('title', 'body', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
    actions = ['publish_contents', 'unpublish_contents']

    def publish_contents(self, request, queryset):
        updated = queryset.update(is_published=True, published_at=timezone.now())
        self.message_user(request, f'{updated} contents were successfully published.')
    publish_contents.short_description = "Publish selected contents"

    def unpublish_contents(self, request, queryset):
        updated = queryset.update(is_published=False, published_at=None)
        self.message_user(request, f'{updated} contents were successfully unpublished.')
    unpublish_contents.short_description = "Unpublish selected contents"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'created_at', 'is_approved', 'short_comment')
    list_filter = ('is_approved', 'created_at', 'content')
    search_fields = ('body', 'author__username', 'content__title')
    actions = ['approve_comments', 'unapprove_comments']

    def short_comment(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    short_comment.short_description = 'Comment'

    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments were successfully approved.')
    approve_comments.short_description = "Approve selected comments"

    def unapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments were successfully unapproved.')
    unapprove_comments.short_description = "Unapprove selected comments"