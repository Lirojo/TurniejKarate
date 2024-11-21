from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,TemplateView
from .models import Athlete, Tournament, Round, WeightCategory
from .forms import RoundForm
class HomeView(TemplateView):
    template_name = 'home.html'  # Szablon strony głównej

@method_decorator(login_required, name='dispatch')
class AthleteListView(ListView):
    model = Athlete
    template_name = 'athlete_list.html'  # Szablon listy zawodników
    context_object_name = 'athletes'

@method_decorator(login_required, name='dispatch')
class AthleteCreateView(CreateView):
    model = Athlete
    template_name = 'athlete_form.html'  # Szablon formularza dodawania zawodnika
    fields = ['first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club', ]
    success_url = reverse_lazy('athlete_list')  # Po dodaniu zawodnika wracamy na listę zawodników

@method_decorator(login_required, name='dispatch')
class AthleteUpdateView(UpdateView):
    model = Athlete
    template_name = 'athlete_form.html'  # Formularz do edycji zawodnika
    fields = ['first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club', ]
    success_url = reverse_lazy('athlete_list')  # Po edycji wracamy na listę zawodników

@method_decorator(login_required, name='dispatch')
class AthleteDeleteView(DeleteView):
    model = Athlete
    template_name = 'athlete_confirm_delete.html'  # Szablon potwierdzenia usunięcia
    success_url = reverse_lazy('athlete_list')  # Po usunięciu wracamy na listę zawodników


class TournamentListView(ListView):
    model = Tournament
    template_name = 'tournament.html'  # Lista turniejów
    context_object_name = 'tournaments'


class TournamentDetailView(TemplateView):
    template_name = 'tournament.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament_id = kwargs.get('tournament_id')
        tournament = get_object_or_404(Tournament, id=tournament_id)
        context['tournament'] = tournament

        # Pobieramy wszystkie rundy dla danego turnieju
        rounds = tournament.rounds.all()

        male_athletes = set()
        female_athletes = set()

        for round_instance in rounds:
            male_athletes.update([round_instance.athlete1, round_instance.athlete2])
            female_athletes.update([round_instance.athlete1, round_instance.athlete2])

        # Grupowanie zawodników według kategorii wagowych
        male_categories = self.group_athletes_by_category(male_athletes)
        female_categories = self.group_athletes_by_category(female_athletes)

        context['male_categories'] = male_categories
        context['female_categories'] = female_categories

        return context

    def group_athletes_by_category(self, athletes):
        categories = {}
        for category in WeightCategory.objects.all():
            athletes_in_category = [athlete for athlete in athletes if athlete.weight_category == category]
            if athletes_in_category:
                categories[category] = athletes_in_category
        return categories

@method_decorator(login_required, name='dispatch')
class RoundCreateView(CreateView):
    model = Round
    template_name = 'round_form.html'
    form_class = RoundForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            athlete1_id = self.request.POST.get('athlete1')
            athlete2_id = self.request.POST.get('athlete2')
            athlete1 = Athlete.objects.filter(id=athlete1_id).first()
            athlete2 = Athlete.objects.filter(id=athlete2_id).first()
            kwargs['athlete1'] = athlete1
            kwargs['athlete2'] = athlete2
        return kwargs

    def form_valid(self, form):
        winner = form.cleaned_data.get('winner')
        if not winner:
            form.add_error('winner', "Please select a winner.")
            return self.form_invalid(form)

        # Usuwamy przegranego zawodnika z turnieju
        athlete1 = form.cleaned_data['athlete1']
        athlete2 = form.cleaned_data['athlete2']
        tournament = form.cleaned_data['tournament']

        loser = athlete1 if winner == athlete2 else athlete2
        tournament.athletes.remove(loser)

        # Zaktualizuj miejsce przegranego
        loser_place = tournament.athletes.count() + 1  # Przyjmujemy, że miejsce to liczba pozostałych + 1
        loser.place = loser_place
        loser.save()

        return super().form_valid(form)

    success_url = reverse_lazy('round_results')

    def form_valid(self, form):
        winner = form.cleaned_data.get('winner')
        if not winner:
            form.add_error('winner', "Please select a winner.")
            return self.form_invalid(form)

        # Usuwamy przegranego zawodnika z turnieju
        athlete1 = form.cleaned_data['athlete1']
        athlete2 = form.cleaned_data['athlete2']
        tournament = form.cleaned_data['tournament']

        loser = athlete1 if winner == athlete2 else athlete2
        tournament.athletes.remove(loser)

        # Zaktualizuj miejsce przegranego (np. w zależności od turnieju)
        loser_place = tournament.athletes.count() + 1  # Przyjmujemy, że miejsce to liczba pozostałych + 1
        loser.save()  # Zakładamy, że przechowujesz miejsce zawodnika w osobnym polu

        return super().form_valid(form)

    success_url = reverse_lazy('round_list')

@method_decorator(login_required, name='dispatch')
class RoundListView(ListView):
    model = Round
    template_name = 'round_list.html'
    context_object_name = 'tournaments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pobieramy wszystkie turnieje
        tournaments = Tournament.objects.prefetch_related('rounds', 'rounds__athlete1', 'rounds__athlete2')

        tournament_data = []
        for tournament in tournaments:
            # Pobierz rundy dla turnieju
            rounds = tournament.rounds.all()

            # Oddziel zawodników na podstawie płci
            male_athletes = set()
            female_athletes = set()

            for round_instance in rounds:
                if round_instance.athlete1.gender == 'M':
                    male_athletes.add(round_instance.athlete1)
                elif round_instance.athlete1.gender == 'F':
                    female_athletes.add(round_instance.athlete1)

                if round_instance.athlete2.gender == 'M':
                    male_athletes.add(round_instance.athlete2)
                elif round_instance.athlete2.gender == 'F':
                    female_athletes.add(round_instance.athlete2)

            # Kategorie wagowe dla mężczyzn
            male_categories = {}
            for category in WeightCategory.objects.all():
                athletes_in_category = [athlete for athlete in male_athletes if athlete.weight_category == category]
                if athletes_in_category:
                    male_categories[category] = athletes_in_category

            # Kategorie wagowe dla kobiet
            female_categories = {}
            for category in WeightCategory.objects.all():
                athletes_in_category = [athlete for athlete in female_athletes if athlete.weight_category == category]
                if athletes_in_category:
                    female_categories[category] = athletes_in_category

            # Dodaj brak kategorii
            male_without_category = [athlete for athlete in male_athletes if athlete.weight_category is None]
            female_without_category = [athlete for athlete in female_athletes if athlete.weight_category is None]

            if male_without_category:
                male_categories["Brak kategorii"] = male_without_category
            if female_without_category:
                female_categories["Brak kategorii"] = female_without_category

            tournament_data.append({
                'tournament': tournament,
                'rounds': rounds,
                'male_categories': male_categories,
                'female_categories': female_categories
            })

        context['tournament_data'] = tournament_data
        return context


def add_round(request):
    if request.method == 'POST':
        form = RoundForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('round_list')  # Przekierowanie na listę rund
        else:
            # Logujemy błędy formularza
            print(form.errors)  # Możesz też użyć logowania
    else:
        form = RoundForm()
    return render(request, 'round_form.html', {'form': form})


def add_athletes_to_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if request.method == 'POST':
        athlete_ids = request.POST.getlist('athletes')  # Pobieramy listę ID zawodników z formularza
        weight_categories = request.POST.getlist('categories')  # Pobieramy listę kategorii dla zawodników

        athletes = Athlete.objects.filter(id__in=athlete_ids)

        # Iterujemy po wszystkich zawodnikach i przypisujemy im kategorię wagową
        for athlete, category_id in zip(athletes, weight_categories):
            category = get_object_or_404(WeightCategory, id=category_id)
            athlete.weight_category = category  # Przypisujemy kategorię wagową zawodnikowi
            athlete.save()  # Zapisujemy zmiany w zawodniku
            tournament.athletes.add(athlete)  # Dodajemy zawodnika do turnieju

        return redirect('tournament_detail', tournament_id=tournament.id)

    else:
        all_athletes = Athlete.objects.all()
        weight_categories = WeightCategory.objects.all()  # Pobieramy wszystkie kategorie wagowe
        return render(request, 'add_athletes.html', {
            'tournament': tournament,
            'athletes': all_athletes,
            'categories': weight_categories,
        })
