from django import forms
from .models import Member

class MemberScoreForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
        }