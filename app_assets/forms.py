from django import forms
from .models import Asset, Category, Location

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white border-white', 'rows': 3}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white border-white', 'rows': 3}),
        }

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'category', 'location', 'assigned_to', 'serial_number', 'model_no', 'make', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'category': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'location': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'assigned_to': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'model_no': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'make': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'notes': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white border-white', 'rows': 3}),
        }
