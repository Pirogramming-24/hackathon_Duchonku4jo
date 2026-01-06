from django import forms
from members.models import Member


class MemberScoreForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["score"]

        widgets = {
            "score": forms.NumberInput(attrs={
                "class": "score-input"
            })
        }
