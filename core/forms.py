from django import forms
from .models import Content, Comment, Category
from django.core.exceptions import ValidationError


class ContentForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect,
        required=False
    )
    new_category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new category name'})
    )

    class Meta:
        model = Content
        fields = ['title', 'body', 'category', 'new_category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your content here'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        self.fields['category'].choices = [(str(c.id), c.name) for c in categories] + [('new', 'Create new category')]

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')

        if category == 'new':
            if not new_category:
                raise ValidationError("Please enter a name for the new category.")
            cleaned_data['category'] = None
        elif not category and not new_category:
            raise ValidationError("Please select a category or create a new one.")

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