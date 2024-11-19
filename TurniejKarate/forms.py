from django import forms
from .models import Round, Athlete, Tournament

class RoundForm(forms.ModelForm):
    class Meta:
        model = Round
        fields = ['tournament', 'athlete1', 'athlete2', 'round_number']
        labels = {
            'tournament': 'Tournament',
            'athlete1': 'Athlete 1',
            'athlete2': 'Athlete 2',
            'round_number': 'Round Number',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['athlete1'].queryset = Athlete.objects.all()
        self.fields['athlete2'].queryset = Athlete.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        tournament = cleaned_data.get("tournament")
        athlete1 = cleaned_data.get("athlete1")
        athlete2 = cleaned_data.get("athlete2")

        if athlete1 and athlete2:
            if athlete1 == athlete2:
                raise forms.ValidationError("Both athletes cannot be the same.")
            if tournament and (athlete1 not in tournament.athletes.all() or athlete2 not in tournament.athletes.all()):
                raise forms.ValidationError("Both athletes must be participants in the selected tournament.")

        return cleaned_data


class RoundForm(forms.ModelForm):
    class Meta:
        model = Round
        fields = ['tournament', 'athlete1', 'athlete2', 'round_number']
        labels = {
            'tournament': 'Tournament',
            'athlete1': 'Athlete 1',
            'athlete2': 'Athlete 2',
            'round_number': 'Round Number',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['athlete1'].queryset = Athlete.objects.all()
        self.fields['athlete2'].queryset = Athlete.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        tournament = cleaned_data.get("tournament")
        athlete1 = cleaned_data.get("athlete1")
        athlete2 = cleaned_data.get("athlete2")

        if tournament and athlete1 and athlete2:
            if not (athlete1 in tournament.athletes.all() and athlete2 in tournament.athletes.all()):
                raise forms.ValidationError("Obaj zawodnicy muszą brać udział w wybranym turnieju.")
        return cleaned_data
