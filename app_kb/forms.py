from django import forms
from .models import Article, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white border-white', 'rows': 3}),
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'category', 'content', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'category': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'content': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white border-white', 'rows': 10}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
