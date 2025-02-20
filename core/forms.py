from django import forms
from .models import Content, Comment, Category
from django.core.exceptions import ValidationError

class ContentForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Content
        fields = ['title', 'body', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your content here'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError("Title must be at least 5 characters long.")
        return title

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) < 100:
            raise ValidationError("Content must be at least 100 characters long.")
        return body

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your comment here'}),
        }

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) < 5:
            raise ValidationError("Comment must be at least 5 characters long.")
        return body