import pytest
from django.urls import reverse
from django.test import Client
from .models import Athlete, Tournament, WeightCategory, Club, Round
from django.contrib.auth.models import User
from .forms import RoundForm
from django.utils import timezone


#-------------------------------------------------------------------
@pytest.fixture
def create_club():
    return Club.objects.create(name="Karate Club")


@pytest.fixture
def create_athletes(create_club):
    club = create_club
    athlete1 = Athlete.objects.create(
        first_name="Jan",
        last_name="Kowalski",
        age=25,
        weight=75.0,
        gender="M",
        belt_level="blue",
        karate_style="shotokan",
        club=club
    )
    athlete2 = Athlete.objects.create(
        first_name="Anna",
        last_name="Nowak",
        age=22,
        weight=65.0,
        gender="F",
        belt_level="green",
        karate_style="goju_ryu",
        club=club
    )
    return athlete1, athlete2


@pytest.fixture
def create_tournament(create_athletes):
    athlete1, athlete2 = create_athletes
    tournament = Tournament.objects.create(
        name="Mistrzostwa Karate",
        type="CHAMPIONSHIP",
        date="2024-12-01"
    )
    tournament.athletes.set([athlete1, athlete2])
    return tournament


@pytest.fixture
def client():
    return Client()


# Test dla widoku listy zawodników
@pytest.mark.django_db
def test_athlete_list_view(client, create_athletes):
    athlete1, athlete2 = create_athletes
    url = reverse('athlete_list')
    response = client.get(url)
    assert response.status_code == 200
    assert athlete1.first_name in response.content.decode()
    assert athlete2.first_name in response.content.decode()


# Test dla widoku tworzenia nowego zawodnika
@pytest.mark.django_db
def test_athlete_create_view(client, create_club):
    club = create_club
    url = reverse('athlete_create')
    data = {
        'first_name': 'Kamil',
        'last_name': 'Zawodnik',
        'age': 20,
        'weight': 70.0,
        'gender': 'M',
        'belt_level': 'white',
        'karate_style': 'shotokan',
        'club': club.id
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Przekierowanie na listę zawodników
    assert Athlete.objects.filter(first_name='Kamil').exists()


# Test dla widoku szczegółowego turnieju
@pytest.mark.django_db
def test_tournament_detail_view(client, create_tournament):
    tournament = create_tournament
    url = reverse('tournament_detail', kwargs={'tournament_id': tournament.id})
    response = client.get(url)
    assert response.status_code == 200
    assert tournament.name in response.content.decode()


# Test dla widoku tworzenia rundy
@pytest.mark.django_db
def test_round_create_view(client, create_tournament, create_athletes):
    tournament = create_tournament
    athlete1, athlete2 = create_athletes
    url = reverse('round_create')
    data = {
        'tournament': tournament.id,
        'athlete1': athlete1.id,
        'athlete2': athlete2.id,
        'round_number': 1
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Przekierowanie na listę rund
    assert Round.objects.filter(tournament=tournament, athlete1=athlete1, athlete2=athlete2).exists()


# Test błędu przy tworzeniu rundy, gdy zawodnicy nie są przypisani do turnieju
@pytest.mark.django_db
def test_round_create_view_with_invalid_athletes(client, create_tournament, create_athletes):
    tournament = create_tournament
    athlete1, athlete2 = create_athletes
    # Odłączymy zawodników od turnieju
    tournament.athletes.clear()
    url = reverse('round_create')
    data = {
        'tournament': tournament.id,
        'athlete1': athlete1.id,
        'athlete2': athlete2.id,
        'round_number': 1
    }
    response = client.post(url, data)
    assert response.status_code == 200  # Powinno wrócić na stronę formularza
    assert "Obaj zawodnicy muszą brać udział w wybranym turnieju." in response.content.decode()


# Test błędu przy tworzeniu rundy, gdy brakuje danych
@pytest.mark.django_db
def test_round_create_view_missing_data(client, create_tournament, create_athletes):
    tournament = create_tournament
    athlete1, athlete2 = create_athletes
    url = reverse('round_create')
    data = {
        'tournament': tournament.id,
        'athlete1': athlete1.id,
        'athlete2': athlete2.id
        # Brak round_number
    }
    response = client.post(url, data)
    assert response.status_code == 200  # Powinno wrócić na stronę formularza
    assert "This field is required." in response.content.decode()
