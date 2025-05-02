from django import forms
from .models import Goal
from .models import JournalEntry
from django.contrib.auth.forms import AuthenticationForm


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title','description']


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['title', 'content']

    def __init__(self, *args, **kwargs):
        super(JournalEntryForm, self).__init__(*args, **kwargs)
        self.fields['content'].initial = ""  # ⬅️ Now it's empty
        self.fields['content'].widget.attrs.update({
            'rows': 15,
            'class': 'form-control',
        })

        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter a short title, e.g. "Gym Check-In"'
        })

        
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Password'
        })
    )