from django import forms
from .models import Article, Category

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'category', 'content', 'attachment', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'category': forms.Select(attrs={'class': 'form-select bg-transparent text-white'}),
            'content': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white', 'rows': 3}),
        }
