# Generated by Django 5.1.3 on 2024-11-18 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TurniejKarate', '0006_alter_athlete_options_alter_club_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='athletes',
            field=models.ManyToManyField(related_name='tournaments', to='TurniejKarate.athlete'),
        ),
    ]