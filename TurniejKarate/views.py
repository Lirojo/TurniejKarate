from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Athlete, Tournament, Round


class HomeView(TemplateView):
    template_name = 'home.html'  # Ścieżka do szablonu strony głównej


class AthleteListView(ListView):
    model = Athlete
    template_name = 'athlete_list.html'  # Ścieżka do szablonu listy zawodników
    context_object_name = 'athletes'  # Nazwa, pod którą lista zawodników będzie dostępna w szablonie


class AthleteCreateView(CreateView):
    model = Athlete
    template_name = 'athlete_form.html'  # Szablon formularza do dodawania zawodnika
    fields = ['first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club', 'tournaments']
    success_url = reverse_lazy('athlete_list')  # Po dodaniu zawodnika wracamy na listę zawodników


class AthleteUpdateView(UpdateView):
    model = Athlete
    template_name = 'athlete_form.html'  # Użyjemy tego samego szablonu co dla tworzenia zawodnika
    fields = ['first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club', 'tournaments']
    success_url = reverse_lazy('athlete_list')  # Po zapisaniu zmian wracamy na listę zawodników


class AthleteDeleteView(DeleteView):
    model = Athlete
    template_name = 'athlete_confirm_delete.html'  # Szablon do potwierdzenia usunięcia zawodnika
    success_url = reverse_lazy('athlete_list')  # Po usunięciu wracamy na listę zawodników


class TournamentView(TemplateView):
    template_name = 'tournament.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pobieramy wszystkie turnieje
        tournaments = Tournament.objects.all()
        context['tournaments'] = tournaments

        # Grupa zawodników z turnieju, podzieleni na płeć i kategorię wagową
        male_athletes = Athlete.objects.filter(gender='M').order_by('weight')
        female_athletes = Athlete.objects.filter(gender='F').order_by('weight')

        # Funkcja do podziału zawodników na kategorie wagowe co 5kg
        def group_by_weight(athletes):
            categories = {}
            for athlete in athletes:
                # Zaokrąglamy wagę do najbliższej liczby całkowitej, będącej wielokrotnością 5
                weight_category = (athlete.weight // 5) * 5
                category_key = f'{weight_category}-{weight_category + 5}kg'
                if category_key not in categories:
                    categories[category_key] = []
                categories[category_key].append(athlete)
            return categories

        # Tworzymy kategorie wagowe dla mężczyzn i kobiet
        context['male_categories'] = group_by_weight(male_athletes)
        context['female_categories'] = group_by_weight(female_athletes)

        return context

