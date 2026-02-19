from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
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
        fields = ['title', 'category', 'content', 'attachment', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'category': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'content': CKEditorUploadingWidget(config_name='default'),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
