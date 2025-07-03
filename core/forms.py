from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import Goal, JournalEntry

User = get_user_model()


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
        label="Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Your email address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary pe-5',
            'placeholder': 'Password'
        })
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            email = email.lower().strip()
            user = authenticate(
                request=self.request,
                email=email,
                password=password
            )

            if user is None:
                raise ValidationError("Invalid email or password. Please try again.")

            # ✅ This is the new check to prevent login if email not verified
            if not user.is_active:
                raise ValidationError("Please confirm your email before logging in.")

            self.user_cache = user

        return self.cleaned_data


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Your email address'
        }),
        help_text="We'll never share your email with anyone."
    )

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

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

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower().strip()
        if commit:
            user.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Your email address'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if not User.objects.filter(email__iexact=email).exists():
            raise ValidationError("No account found with this email.")
        return email
