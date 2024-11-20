from django.db import models
from django.core.exceptions import ValidationError


class WeightCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    min_weight = models.DecimalField(max_digits=5, decimal_places=2)
    max_weight = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.min_weight}kg - {self.max_weight}kg)"


class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Athlete(models.Model):
    BELT_LEVELS = [
        ('white', 'White'),
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('brown', 'Brown'),
        ('black', 'Black'),
    ]

    KARATE_STYLES = [
        ('shotokan', 'Shotokan'),
        ('goju_ryu', 'Goju-Ryu'),
        ('shito_ryu', 'Shito-Ryu'),
        ('kyokushin', 'Kyokushin'),
        ('wado_ryu', 'Wado-Ryu'),
        ('enshin', 'Enshin'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    belt_level = models.CharField(max_length=10, choices=BELT_LEVELS)
    karate_style = models.CharField(max_length=20, choices=KARATE_STYLES)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    weight_category = models.ForeignKey(WeightCategory, on_delete=models.SET_NULL, null=True, blank=True)
    place = models.PositiveIntegerField(null=True, blank=True)  # Pozycja w turnieju

    def clean(self):
        # Walidacja, by waga zawodnika była zgodna z kategorią wagową
        if self.weight_category and not (
                self.weight_category.min_weight <= self.weight <= self.weight_category.max_weight
        ):
            raise ValidationError(
                f"Zawodnik musi mieć wagę w przedziale {self.weight_category.min_weight}kg - {self.weight_category.max_weight}kg dla kategorii {self.weight_category.name}"
            )
        super().clean()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.belt_level.capitalize()} Belt ({self.karate_style.capitalize()})"


class Tournament(models.Model):
    TOURNAMENT_TYPES = [
        ('CHAMPIONSHIP', 'Championship'),
        ('REGIONAL', 'Regional'),
        ('CLUB', 'Club Tournament'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TOURNAMENT_TYPES, default='CLUB')
    date = models.DateField()
    athletes = models.ManyToManyField(Athlete, related_name='tournaments')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='rounds')
    athlete1 = models.ForeignKey('Athlete', on_delete=models.CASCADE, related_name='rounds_as_athlete1')
    athlete2 = models.ForeignKey('Athlete', on_delete=models.CASCADE, related_name='rounds_as_athlete2')
    winner = models.ForeignKey('Athlete', on_delete=models.SET_NULL, null=True, blank=True, related_name='rounds_won')
    round_number = models.PositiveIntegerField()

    def set_winner(self, winner_athlete):
        """Ustaw zwycięzcę rundy"""
        if winner_athlete != self.athlete1 and winner_athlete != self.athlete2:
            raise ValueError("Zwycięzca musi być jednym z zawodników w rundzie.")
        self.winner = winner_athlete
        self.save()

    def save(self, *args, **kwargs):
        if self.winner:
            # Przegrany zawodnik odpada z turnieju
            loser = self.athlete2 if self.winner == self.athlete1 else self.athlete1
            self.tournament.athletes.remove(loser)

            # Przypisanie miejsca przegranemu
            total_athletes = self.tournament.athletes.count() + 1  # +1 bo przegrany jest usuwany
            loser.place = total_athletes
            loser.save()

        super().save(*args, **kwargs)

    def __str__(self):
        winner = self.winner if self.winner else "No Winner"
        return f"Round {self.round_number} - {self.athlete1} vs {self.athlete2} (Winner: {winner})"


class Coach(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='coaches')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.club.name}"
