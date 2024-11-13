from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from .models import Athlete, Tournament, Round, WeightCategory


class HomeView(TemplateView):
    template_name = 'home.html'  # Szablon strony głównej


class AthleteListView(ListView):
    model = Athlete
    template_name = 'athlete_list.html'  # Szablon listy zawodników
    context_object_name = 'athletes'


class AthleteCreateView(CreateView):
    model = Athlete
    template_name = 'athlete_form.html'  # Szablon formularza dodawania zawodnika
    fields = ['first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club', 'tournaments']
    success_url = reverse_lazy('athlete_list')  # Po dodaniu zawodnika wracamy na listę zawodników


class AthleteUpdateView(UpdateView):
    model = Athlete
    template_name = 'athlete_form.html'  # Formularz do edycji zawodnika
    fields = ['first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club', 'tournaments']
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

        # Pobieramy zawodników przypisanych do turnieju
        male_athletes = Athlete.objects.filter(tournaments=tournament, gender='M')
        female_athletes = Athlete.objects.filter(tournaments=tournament, gender='F')

        # Przygotowanie kategorii wagowych dla mężczyzn i kobiet
        weight_categories = WeightCategory.objects.all()

        # Kategoria wagowa dla mężczyzn
        male_categories = {}
        for category in weight_categories:
            athletes_in_category = male_athletes.filter(weight_category=category)
            if athletes_in_category.exists():
                male_categories[category] = athletes_in_category

        # Kategoria wagowa dla kobiet
        female_categories = {}
        for category in weight_categories:
            athletes_in_category = female_athletes.filter(weight_category=category)
            if athletes_in_category.exists():
                female_categories[category] = athletes_in_category

        # Zawodnicy bez przypisanej kategorii wagowej (zarówno dla mężczyzn, jak i kobiet)
        male_without_category = male_athletes.filter(weight_category__isnull=True)
        female_without_category = female_athletes.filter(weight_category__isnull=True)

        if male_without_category.exists():
            male_categories["Brak kategorii"] = male_without_category
        if female_without_category.exists():
            female_categories["Brak kategorii"] = female_without_category

        context['male_categories'] = male_categories
        context['female_categories'] = female_categories

        return context


class RoundCreateView(CreateView):
    model = Round
    template_name = 'round_form.html'
    fields = ['tournament', 'athlete1', 'athlete2', 'round_number', 'winner']

    def form_valid(self, form):
        # Logika do zapisania wyniku rundy i ewentualne ustawienie zwycięzcy
        return super().form_valid(form)
