from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from autoslug import AutoSlugField

class User(AbstractUser):
    ROLES = (
        ('admin', 'Administrator'),
        ('editor', 'Editor'),
        ('author', 'Author'),
        ('viewer', 'Viewer'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='viewer')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Content(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contents')
    categories = models.ManyToManyField(Category, related_name='contents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    featured_image = models.ImageField(upload_to='content_images/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def publish(self):
        self.published_at = timezone.now()
        self.is_published = True
        self.save()

    def unpublish(self):
        self.is_published = False
        self.published_at = None
        self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if Content.objects.filter(slug=self.slug).exists():
            self.slug = f"{self.slug}-{Content.objects.count() + 1}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('content_detail', kwargs={'slug': self.slug})

class Comment(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.content}'

    def approve(self):
        self.is_approved = True
        self.save()