from django import forms
from .models import Content, Comment, Category, Document
from django.core.exceptions import ValidationError


class ContentForm(forms.ModelForm):
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
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your content here'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        categories = cleaned_data.get('categories')
        new_category = cleaned_data.get('new_category')

        if not categories and not new_category:
            raise ValidationError("Please select at least one category or create a new one.")

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
    class Meta:
        model = Document
        fields = ['file', 'title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter document title'}),
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    file = forms.FileField(required=False)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError("File size cannot exceed 10MB.")
        return file

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        file = cleaned_data.get('file')

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