from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreateForm(forms.ModelForm):
    initial_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-transparent text-white border-white'}),
        label="Initial Password",
        help_text="Set a temporary password for the user."
    )

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

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['initial_password']
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
