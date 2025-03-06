from django.db import models, migrations, transaction
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import JSONField
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('pageadmin', 'Page Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='pageadmin')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['user_type']),
        ]

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        

class Content(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True, blank=True)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contents')
    categories = models.ManyToManyField(Category, related_name='contents', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=True) 
    views = models.PositiveIntegerField(default=0)
    featured_image = models.ImageField(upload_to='content_images/', null=True, blank=True)
    metadata = JSONField(default=dict)
    search_vector = SearchVectorField(null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['created_at']),
            models.Index(fields=['published_at']),
            GinIndex(fields=['search_vector']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(published_at__isnull=False) | models.Q(is_published=False),
                name='published_content_must_have_published_at'
            )
        ]

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
            self.slug = self.generate_unique_slug()
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        base_slug = slugify(self.title)
        unique_slug = base_slug
        counter = 1
        while Content.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        return unique_slug

    def get_absolute_url(self):
        return reverse('content_detail', kwargs={'slug': self.slug})
    
class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)  #optional
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['uploaded_at']),
        ]

class Comment(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['is_approved']),
        ]

    def __str__(self):
        return f'Comment by {self.author} on {self.content}'

    def approve(self):
        self.is_approved = True
        self.save()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_your_previous_migration'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION update_content_modified(content_id INTEGER)
            RETURNS VOID AS $$
            BEGIN
                UPDATE core_content SET updated_at = NOW() WHERE id = content_id;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="""
            DROP FUNCTION IF EXISTS update_content_modified(content_id INTEGER);
            """
        )
    ]