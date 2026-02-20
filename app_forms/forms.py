from django import forms
from .models import CustomForm, FormQuestion

class CustomFormCreateForm(forms.ModelForm):
    class Meta:
        model = CustomForm
        fields = ['title', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FormQuestionCreateForm(forms.ModelForm):
    class Meta:
        model = FormQuestion
        fields = ['question_text', 'question_type', 'choices', 'is_required', 'order']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'question_type': forms.Select(attrs={'class': 'form-select bg-transparent text-white'}),
            'choices': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white', 'rows': 2, 'placeholder': 'Option 1, Option 2, Option 3'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control bg-transparent text-white'}),
        }
