from django import forms
from .models import Asset, Category, Location
import json

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
    specifications_json = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control bg-transparent text-white border-white', 'rows': 5, 'placeholder': '{"key": "value"}'}),
        required=False,
        label="Specifications (JSON)",
        help_text="Enter valid JSON key-value pairs."
    )

    class Meta:
        model = Asset
        fields = ['name', 'category', 'location', 'assigned_to', 'serial_number', 'model_no', 'make', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'category': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'location': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'model_no': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'make': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'notes': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white border-white', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.specifications:
            self.fields['specifications_json'].initial = json.dumps(self.instance.specifications, indent=2)

    def clean_specifications_json(self):
        data = self.cleaned_data['specifications_json']
        if not data:
            return {}
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON format")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.specifications = self.cleaned_data['specifications_json']
        if commit:
            instance.save()
        return instance
