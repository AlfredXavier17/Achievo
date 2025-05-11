from django import forms
from .models import Goal, JournalEntry
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm  # Add PasswordResetForm
from django.contrib.auth.models import User

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'description']

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['title', 'content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].initial = ""
        self.fields['content'].widget.attrs.update({
            'rows': 15,
            'class': 'form-control bg-dark text-light border-secondary',
        })
        self.fields['title'].widget.attrs.update({
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Enter a short title, e.g. "Gym Check-In"'
        })

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary pe-5',
            'placeholder': 'Password'
        })
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Your email address'
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Create password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Confirm password'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Choose a username'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        if commit:
            user.save()
        return user

# Add CustomPasswordResetForm to require username and email match
class CustomPasswordResetForm(PasswordResetForm):
    username = forms.CharField(max_length=150, required=True)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')

        if email and username:
            try:
                user = User.objects.get(username=username)
                if user.email != email:
                    raise forms.ValidationError("The username and email do not match.")
            except User.DoesNotExist:
                # Silently fail to prevent username enumeration
                pass
        return cleaned_data