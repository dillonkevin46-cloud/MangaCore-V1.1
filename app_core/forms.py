from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
