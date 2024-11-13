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
