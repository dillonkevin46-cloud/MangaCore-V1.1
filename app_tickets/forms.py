from django import forms
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Ticket, Comment

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'status', 'priority', 'assigned_agent', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
            # description uses CKEditorUploadingWidget, we don't need 'class': 'form-control' as ckeditor handles its own styling usually,
            # but we can try to apply some attrs if needed. Usually ckeditor replaces the textarea.
            'description': CKEditorUploadingWidget(config_name='default'),
            'status': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'priority': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'assigned_agent': forms.Select(attrs={'class': 'form-select bg-transparent text-white border-white'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not user or not user.is_staff:
            if 'assigned_agent' in self.fields:
                del self.fields['assigned_agent']
            if 'status' in self.fields:
                del self.fields['status']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'is_public']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control bg-transparent text-white border-white', 'rows': 3}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
