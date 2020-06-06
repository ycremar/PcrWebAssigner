from django import forms
from django.utils import timezone
from PcrWebAssigner.models import RealDamage

class damage_report_form(forms.ModelForm):
    class Meta:
        model = RealDamage
        exclude = ['player', 'boss', 'bonus', 'report_time']
        widgets = {
            'damage': forms.NumberInput(attrs = {'class': 'w3-input w3-cell', 'style': 'width:75%'}),
            'notes': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        }