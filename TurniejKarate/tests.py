import pytest
from django.urls import reverse
from django.test import Client
from django.core.exceptions import ValidationError
from TurniejKarate.models import Tournament, Athlete, Round, Club, WeightCategory
from TurniejKarate.forms import RoundForm
from django.contrib.auth.models import User


@pytest.fixture
def user():
    user = User.objects.create_user(username='testuser', password='password')
    return user


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


@pytest.mark.django_db
def test_round_form_valid_data(athlete1, athlete2, tournament):
    from TurniejKarate.forms import RoundForm

    # Sprawdzamy, czy zawodnicy mają różną płeć
    athlete1.gender = "M"
    athlete2.gender = "F"
    athlete1.save()
    athlete2.save()

    form_data = {
        'tournament': tournament.id,
        'athlete1': athlete1.id,
        'athlete2': athlete2.id,
        'round_number': 1,
        'winner': athlete1.id,
    }
    form = RoundForm(data=form_data)

    # Konfigurujemy queryset dla pola winner
    form.fields['winner'].queryset = Athlete.objects.filter(id__in=[athlete1.id, athlete2.id])

    # Sprawdzamy, czy formularz jest nieprawidłowy
    assert not form.is_valid(), form.errors  # Formularz powinien być nieprawidłowy, ponieważ płeć zawodników się różni
    assert 'Mężczyzna nie może walczyć z kobietą. Muszą walczyć mężczyźni z mężczyznami lub kobiety z kobietami.' in \
           form.errors['__all__']


@pytest.mark.django_db
def test_round_form_invalid_winner(athlete1, athlete2, tournament):
    form_data = {
        'tournament': tournament.id,
        'athlete1': athlete1.id,
        'athlete2': athlete2.id,
        'round_number': 1,
        'winner': None,  # Invalid as no winner is selected
    }
    form = RoundForm(data=form_data)

    # Symulujemy przypisanie zawodników do formularza
    form.fields['winner'].queryset = Athlete.objects.filter(id__in=[athlete1.id, athlete2.id])

    assert not form.is_valid()

    # Sprawdzamy, czy błędy formularza zawierają odpowiednie komunikaty
    assert '__all__' in form.errors
    assert 'Winner must be either Athlete 1 or Athlete 2.' in form.errors['__all__']
    assert 'Mężczyzna nie może walczyć z kobietą. Muszą walczyć mężczyźni z mężczyznami lub kobiety z kobietami.' in \
           form.errors['__all__']


@pytest.mark.django_db
def test_round_create_view_get(client, tournament, athlete1, athlete2, user):
    # Zalogowanie użytkownika przed wysłaniem zapytania
    client.login(username=user.username, password='password')  # Użyj odpowiednich danych użytkownika

    url = reverse('round_create')
    response = client.get(url)

    # Sprawdzenie, czy status odpowiedzi to 200
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.template_name == ['round_form.html']


@pytest.mark.django_db
def test_round_create_view_post_invalid(client, tournament, athlete1, athlete2, user):
    # Zalogowanie użytkownika przed wysłaniem zapytania
    client.login(username=user.username, password='password')  # Użyj odpowiednich danych użytkownika

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


@pytest.mark.django_db
def test_athlete_weight_validation():
    category = WeightCategory.objects.create(name="Lightweight", min_weight=60, max_weight=70)
    athlete = Athlete(
        first_name="Invalid",
        last_name="Athlete",
        age=30,
        weight=75.0,  # Waga poza zakresem
        gender="M",
        belt_level="blue",
        karate_style="shotokan",
        weight_category=category,
    )
    with pytest.raises(ValidationError):
        athlete.clean()


@pytest.mark.django_db
def test_round_no_winner(client, tournament, athlete1, athlete2):
    round_ = Round(
        tournament=tournament,
        athlete1=athlete1,
        athlete2=athlete2,
        round_number=1,
        winner=None,
    )
    with pytest.raises(ValueError):
        round_.set_winner(None)


@pytest.mark.django_db
def test_add_athletes_to_tournament(client, tournament, athlete1, athlete2):
    url = reverse('add_athletes_to_tournament', args=[tournament.id])
    response = client.post(url, {'athletes': [athlete1.id, athlete2.id]})
    assert response.status_code == 302
    assert tournament.athletes.count() == 0


@pytest.mark.django_db
def test_tournament_detail_invalid_id(client):
    url = reverse('tournament_detail', args=[9999])  # Nieistniejący turniej
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_male_female_cannot_fight(client, tournament, athlete1, athlete2):
    # Przygotowanie zawodników - athlete1 to mężczyzna, athlete2 to kobieta
    athlete1.gender = "M"
    athlete2.gender = "F"
    athlete1.save()
    athlete2.save()

    round_ = Round(
        tournament=tournament,
        athlete1=athlete1,
        athlete2=athlete2,
        round_number=1,
        winner=None,
    )

    with pytest.raises(ValidationError):
        round_.clean()  # Powinien rzucić błąd walidacji


@pytest.mark.django_db
def test_different_weight_categories_cannot_fight(client, tournament, athlete1, athlete2):
    # Przygotowanie zawodników z różnych kategorii wagowych
    category1 = WeightCategory.objects.create(name="Lightweight", min_weight=60, max_weight=70)
    category2 = WeightCategory.objects.create(name="Heavyweight", min_weight=80, max_weight=100)

    athlete1.weight_category = category1
    athlete2.weight_category = category2
    athlete1.save()
    athlete2.save()

    round_ = Round(
        tournament=tournament,
        athlete1=athlete1,
        athlete2=athlete2,
        round_number=1,
        winner=None,
    )

    with pytest.raises(ValidationError):
        round_.clean()  # Powinien rzucić błąd walidacji


@pytest.mark.django_db
def test_male_vs_male_can_fight(client, tournament, athlete1, athlete2):
    # Przygotowanie dwóch mężczyzn
    athlete1.gender = "M"
    athlete2.gender = "M"
    athlete1.save()
    athlete2.save()

    round_ = Round(
        tournament=tournament,
        athlete1=athlete1,
        athlete2=athlete2,
        round_number=1,
        winner=None,
    )

    # Sprawdzamy, że walka się odbędzie bez błędów
    try:
        round_.clean()  # Nie powinno rzucić błędu
    except ValidationError:
        pytest.fail("Test failed: Male vs Male should be allowed")


@pytest.mark.django_db
def test_female_vs_female_can_fight(client, tournament, athlete1, athlete2):
    # Przygotowanie dwóch kobiet
    athlete1.gender = "F"
    athlete2.gender = "F"
    athlete1.save()
    athlete2.save()

    round_ = Round(
        tournament=tournament,
        athlete1=athlete1,
        athlete2=athlete2,
        round_number=1,
        winner=None,
    )

    # Sprawdzamy, że walka się odbędzie bez błędów
    try:
        round_.clean()  # Nie powinno rzucić błędu
    except ValidationError:
        pytest.fail("Test failed: Female vs Female should be allowed")
