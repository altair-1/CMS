from django import forms
from .models import Content, Document, Category, Comment
from django.core.exceptions import ValidationError


class ContentForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        required=True,
        error_messages={'required': 'Please enter a title for your content'},
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'})
    )
    
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    
    new_category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new category name'})
    )

    class Meta:
        model = Content
        fields = ['title', 'body', 'categories', 'new_category']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your content here'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        categories = cleaned_data.get('categories')
        new_category = cleaned_data.get('new_category')
        
        # Check if a category was selected from the dropdown
        category_id = self.data.get('category')
        
        # Skip validation if this is an edit of existing content with categories
        if self.instance and self.instance.pk and self.instance.categories.exists():
            return cleaned_data
            
        # Only validate if neither categories nor dropdown category nor new category is provided
        if not categories and not new_category and not (category_id and category_id != 'new'):
            raise ValidationError("Please select at least one category or create a new one.")

        # Handle new category creation
        if new_category:
            category, created = Category.objects.get_or_create(name=new_category)
            if not categories:
                cleaned_data['categories'] = [category]
            else:
                cleaned_data['categories'] = list(categories) + [category]

        return cleaned_data

    def clean_featured_image(self):
        featured_image = self.cleaned_data.get('featured_image')
        if featured_image:
            if featured_image.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Image file size cannot exceed 5MB.")
        return featured_image


class DocumentForm(forms.ModelForm):
    file = forms.FileField(required=False)
    title = forms.CharField(required=False)

    class Meta:
        model = Document
        fields = ['file', 'title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter document title'}),
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError("File size cannot exceed 10MB.")
        return file

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        title = cleaned_data.get('title')

        if file and not title:
            raise ValidationError("Please provide a title for the uploaded document.")

        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        labels = {
            'body': '',  # This removes the label
        }
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your comment here'}),
        }

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) < 5:
            raise ValidationError("Comment must be at least 5 characters long.")
        return body