from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Category, Content, Comment

User = get_user_model()

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.content = Content.objects.create(
            title='Test Content',
            slug='test-content',
            body='This is test content',
            author=self.user
        )
        self.content.categories.add(self.category)

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Test Category')

    def test_content_str(self):
        self.assertEqual(str(self.content), 'Test Content')

    def test_comment_creation(self):
        comment = Comment.objects.create(
            content=self.content,
            author=self.user,
            body='This is a test comment'
        )
        self.assertEqual(str(comment), f'Comment by {self.user} on {self.content}')

# Add more tests for views, forms, etc.