from django import forms
from .models import Asset, Category, Location

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name', 'category', 'location', 'assigned_to', 'ip_address',
            'is_monitored', 'alert_email', 'serial_number', 'model_no',
            'make', 'specifications', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'category': forms.Select(attrs={'class': 'form-select bg-transparent text-white'}),
            'location': forms.Select(attrs={'class': 'form-select bg-transparent text-white'}),
            'assigned_to': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'is_monitored': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alert_email': forms.EmailInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'model_no': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'make': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white', 'rows': 5, 'placeholder': '{"key": "value"}'}),
            'notes': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white', 'rows': 3}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white', 'rows': 3}),
        }

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white', 'rows': 3}),
        }
