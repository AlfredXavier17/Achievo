from django import forms
from .models import Goal
from .models import JournalEntry


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
        self.fields['content'].initial = (
            "WHAT DID I DO TODAY THAT MOVED ME CLOSER TO MY GOAL?\n\n"
            "WHAT OBSTACLES OR CHALLENGES DID I FACE TODAY?\n\n"
            "WHAT WILL I DO DIFFERENTLY OR IMPROVE TOMORROW?\n\n"
        )
        self.fields['content'].widget.attrs.update({
            'rows': 15,
            'class': 'form-control',
        })   

        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter a short title, e.g. "Gym Check-In"'
        })