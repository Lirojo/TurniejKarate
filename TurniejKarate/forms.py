from django import forms
from .models import Round, Athlete, Tournament


class RoundForm(forms.ModelForm):
    class Meta:
        model = Round
        fields = ['tournament', 'athlete1', 'athlete2', 'round_number', 'winner']
        labels = {
            'tournament': 'Tournament',
            'athlete1': 'Athlete 1',
            'athlete2': 'Athlete 2',
            'round_number': 'Round Number',
            'winner': 'Winner',
        }

    def __init__(self, *args, **kwargs):
        # Pobieramy dodatkowe dane przekazane do formularza
        athlete1 = kwargs.pop('athlete1', None)
        athlete2 = kwargs.pop('athlete2', None)
        super().__init__(*args, **kwargs)

        # Pole `winner` na początku jest puste
        self.fields['winner'].queryset = Athlete.objects.none()

        if athlete1 and athlete2:
            # Ograniczamy wybór zwycięzcy do wybranych zawodników
            self.fields['winner'].queryset = Athlete.objects.filter(id__in=[athlete1.id, athlete2.id])

    def clean(self):
        cleaned_data = super().clean()
        athlete1 = cleaned_data.get("athlete1")
        athlete2 = cleaned_data.get("athlete2")
        winner = cleaned_data.get("winner")

        # Walidacja: zwycięzca musi należeć do uczestników rundy
        if winner not in [athlete1, athlete2]:
            raise forms.ValidationError("Winner must be either Athlete 1 or Athlete 2.")

        # Walidacja: zawodnicy muszą być w tej samej kategorii wagowej
        if athlete1 and athlete2 and athlete1.weight_category != athlete2.weight_category:
            raise forms.ValidationError("Athletes must belong to the same weight category.")

        return cleaned_data
