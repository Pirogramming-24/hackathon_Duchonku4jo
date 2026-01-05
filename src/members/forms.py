# members/forms.py
from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'gender', 'major']
        labels = {
            'name': '이름',
            'gender': '성별',
            'major': '전공자 여부',
        }
