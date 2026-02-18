from django import forms
from .models import Ticket, Comment

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'status', 'priority', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white border-white', 'rows': 5}),
            'status': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'priority': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'is_public']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white border-white', 'rows': 3}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
