from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy,reverse
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from .models import Athlete, Tournament, Round, WeightCategory
from .forms import RoundForm


class HomeView(TemplateView):
    template_name = 'home.html'  # Szablon strony głównej


class AthleteListView(ListView):
    model = Athlete
    template_name = 'athlete_list.html'  # Szablon listy zawodników
    context_object_name = 'athletes'


class AthleteCreateView(CreateView):
    model = Athlete
    template_name = 'athlete_form.html'  # Szablon formularza dodawania zawodnika
    fields = ['first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club',]
    success_url = reverse_lazy('athlete_list')  # Po dodaniu zawodnika wracamy na listę zawodników


class AthleteUpdateView(UpdateView):
    model = Athlete
    template_name = 'athlete_form.html'  # Formularz do edycji zawodnika
    fields = ['first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club',]
    success_url = reverse_lazy('athlete_list')  # Po edycji wracamy na listę zawodników


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


class RoundCreateView(CreateView):
    model = Round
    template_name = 'round_form.html'
    fields = ['tournament', 'athlete1', 'athlete2', 'round_number']

    def form_valid(self, form):
        athlete1 = form.cleaned_data['athlete1']
        athlete2 = form.cleaned_data['athlete2']
        tournament = form.cleaned_data['tournament']

        # Sprawdzamy, czy obaj zawodnicy są przypisani do turnieju
        if athlete1 not in tournament.athletes.all() or athlete2 not in tournament.athletes.all():
            form.add_error(None, "Obaj zawodnicy muszą brać udział w wybranym turnieju.")
            return self.form_invalid(form)

        return super().form_valid(form)

    success_url = reverse_lazy('round_list')


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
