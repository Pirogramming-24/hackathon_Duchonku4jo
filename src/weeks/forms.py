from django import forms
from .models import Week

class WeekForm(forms.ModelForm):
    class Meta:
        model = Week
        fields = [
            "week_no",
            "pr_name",
            "team_count",
        ]
        labels = {
            "week_no": "주차",
            "pr_name": "과제명",
            "team_count": "팀 개수"
        }
        
    def __init__(self, *args, **kwargs):
        next_week_no = kwargs.pop("next_week_no", None)
        super().__init__(*args, **kwargs)

        if next_week_no is not None:
            self.fields["week_no"].initial = next_week_no
            self.fields["week_no"].disabled = True