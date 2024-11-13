from django.db import models


class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Club"
        verbose_name_plural = "Clubs"


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
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # w kilogramach
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    belt_level = models.CharField(max_length=10, choices=BELT_LEVELS)
    karate_style = models.CharField(max_length=20, choices=KARATE_STYLES)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=False)
    tournaments = models.ManyToManyField('Tournament', related_name='athletes', blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.belt_level.capitalize()} Belt ({self.karate_style.capitalize()})"

    class Meta:
        verbose_name = "Athlete"
        verbose_name_plural = "Athletes"


class Coach(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='coaches')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.club.name}"

    class Meta:
        verbose_name = "Coach"
        verbose_name_plural = "Coaches"


from django.db import models


class Tournament(models.Model):
    TOURNAMENT_TYPES = [
        ('CHAMPIONSHIP', 'Championship'),
        ('REGIONAL', 'Regional'),
        ('CLUB', 'Club Tournament'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TOURNAMENT_TYPES, default='CLUB')
    date = models.DateField()

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
        if winner_athlete == self.athlete1 or winner_athlete == self.athlete2:
            self.winner = winner_athlete
            self.save()
        else:
            raise ValueError("Winner must be one of the athletes in the round.")

    def __str__(self):
        return f"Round {self.round_number} - {self.athlete1} vs {self.athlete2} (Winner: {self.winner})"
