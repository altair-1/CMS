from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLES = (
        ('admin', 'Administrator'),
        ('editor', 'Editor'),
        ('author', 'Author'),
        ('viewer', 'Viewer'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='viewer')

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Content(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name='contents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    def publish(self):
        self.published_at = timezone.now()
        self.is_published = True
        self.save()

    def __str__(self):
        return self.title

class Comment(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f'Comment by {self.author} on {self.content}'