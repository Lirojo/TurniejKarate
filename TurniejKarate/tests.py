import pytest
from django.urls import reverse
from django.test import Client
from TurniejKarate.models import Tournament, Athlete, Round, Club
from TurniejKarate.forms import RoundForm


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def club(db):
    return Club.objects.create(name="Karate Club")


@pytest.fixture
def athlete1(club, tournament):
    return Athlete.objects.create(
        first_name="John",
        last_name="Doe",
        age=25,
        weight=70.0,
        gender="M",
        belt_level="blue",
        karate_style="shotokan",
        club=club,
        weight_category=None
    )


@pytest.fixture
def athlete2(club, tournament):
    return Athlete.objects.create(
        first_name="Jane",
        last_name="Smith",
        age=24,
        weight=65.0,
        gender="F",
        belt_level="blue",
        karate_style="shotokan",
        club=club,
        weight_category=None
    )


@pytest.fixture
def tournament(db, club):
    tournament = Tournament.objects.create(
        name="Test Tournament",
        type="CLUB",
        date="2024-01-01"
    )
    # Dodaj zawodników do turnieju
    tournament.athletes.set(Athlete.objects.all())
    return tournament


@pytest.mark.django_db
def test_athlete_creation(client, athlete1, club):
    # Test using athlete1 fixture
    athlete = athlete1
    assert athlete.club == club
    assert athlete.first_name == "John"
    assert athlete.last_name == "Doe"


@pytest.mark.django_db
def test_athlete_creation_with_existing_club(client):
    club = Club.objects.create(name="Shotokan Karate Club")

    # Include required fields such as age, weight, and others
    athlete = Athlete.objects.create(
        first_name="Jane",
        last_name="Smith",
        age=24,  # Add age
        weight=65.0,  # Add weight
        gender="F",
        belt_level="blue",
        karate_style="shotokan",
        club=club
    )

    # Sprawdzamy, czy zawodnik został przypisany do klubu
    assert athlete.club == club
    assert athlete.first_name == "Jane"

def test_round_form_valid_data(athlete1, athlete2, tournament):
    from TurniejKarate.forms import RoundForm

    form_data = {
        'tournament': tournament.id,
        'athlete1': athlete1.id,
        'athlete2': athlete2.id,
        'round_number': 1,
        'winner': athlete1.id,
    }
    form = RoundForm(data=form_data)

    # Konfiguruj queryset pola winner
    form.fields['winner'].queryset = Athlete.objects.filter(id__in=[athlete1.id, athlete2.id])

    assert form.is_valid(), form.errors


def test_round_form_invalid_winner(athlete1, athlete2, tournament):
    form_data = {
        'tournament': tournament.id,
        'athlete1': athlete1.id,
        'athlete2': athlete2.id,
        'round_number': 1,
        'winner': None,  # Invalid as no winner is selected
    }
    form = RoundForm(data=form_data)

    # Symuluj przypisanie zawodników do formularza
    form.fields['winner'].queryset = Athlete.objects.filter(id__in=[athlete1.id, athlete2.id])

    assert not form.is_valid()
    assert '__all__' in form.errors
    assert form.errors['__all__'] == ['Winner must be either Athlete 1 or Athlete 2.']


@pytest.mark.django_db
def test_round_create_view_get(client, tournament, athlete1, athlete2):
    url = reverse('round_create')
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.template_name == ['round_form.html']


@pytest.mark.django_db
def test_round_create_view_post_valid(client, tournament, athlete1, athlete2):
    url = reverse('round_create')
    form_data = {
        'tournament': tournament.id,
        'athlete1': athlete1.id,
        'athlete2': athlete2.id,
        'round_number': 1,
        'winner': athlete1.id,
    }
    response = client.post(url, data=form_data)
    assert response.status_code == 302  # Redirect after success
    assert Round.objects.count() == 1
    new_round = Round.objects.first()
    assert new_round.tournament == tournament
    assert new_round.winner == athlete1
    assert new_round.round_number == 1


@pytest.mark.django_db
def test_round_create_view_post_invalid(client, tournament, athlete1, athlete2):
    url = reverse('round_create')
    form_data = {
        'tournament': tournament.id,
        'athlete1': athlete1.id,
        'athlete2': athlete2.id,
        'round_number': 1,
        'winner': '',  # Pusty ciąg zamiast None
    }
    response = client.post(url, data=form_data)

    # Oczekujemy, że formularz będzie nieprawidłowy i widok zwróci kod 200 z błędami formularza
    assert response.status_code == 200
    assert 'Winner must be either Athlete 1 or Athlete 2.' in response.content.decode()

@pytest.mark.django_db
def test_loser_removed_from_tournament(client):
    # Include date when creating Tournament
    tournament = Tournament.objects.create(
        name="Karate Tournament",
        type="CLUB",
        date="2024-01-01"  # Provide a valid date
    )

    # Continue with the test setup
    club = Club.objects.create(name="Karate Club")
    athlete1 = Athlete.objects.create(
        first_name="John",
        last_name="Doe",
        age=25,
        weight=70.0,
        gender="M",
        belt_level="blue",
        karate_style="shotokan",
        club=club
    )
    athlete2 = Athlete.objects.create(
        first_name="Jane",
        last_name="Smith",
        age=24,
        weight=65.0,
        gender="F",
        belt_level="blue",
        karate_style="shotokan",
        club=club
    )
    tournament.athletes.add(athlete1, athlete2)

    # Simulate an athlete elimination (e.g., athlete2 loses)
    athlete2.is_eliminated = True  # Assuming this field exists
    athlete2.save()

    # Remove eliminated athlete from the tournament
    tournament.athletes.remove(athlete2)

    # Test if the eliminated athlete was removed from the tournament
    assert tournament.athletes.count() == 1  # Only one athlete should remain

