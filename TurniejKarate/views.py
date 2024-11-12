from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from .models import Athlete

class HomeView(TemplateView):
    template_name = 'home.html'  # Ścieżka do szablonu strony głównej


class AthleteListView(ListView):
    model = Athlete
    template_name = 'athlete_list.html'  # Ścieżka do szablonu listy zawodników
    context_object_name = 'athletes'  # Nazwa, pod którą lista zawodników będzie dostępna w szablonie

class AthleteCreateView(CreateView):
    model = Athlete
    template_name = 'athlete_form.html'  # Szablon formularza do dodawania zawodnika
    fields = ['first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club']
    success_url = reverse_lazy('athlete_list')  # Po dodaniu zawodnika wracamy na listę zawodników

class AthleteUpdateView(UpdateView):
    model = Athlete
    template_name = 'athlete_form.html'  # Użyjemy tego samego szablonu co dla tworzenia zawodnika
    fields = ['first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club']
    success_url = reverse_lazy('athlete_list')  # Po zapisaniu zmian wracamy na listę zawodników

class AthleteDeleteView(DeleteView):
    model = Athlete
    template_name = 'athlete_confirm_delete.html'  # Szablon do potwierdzenia usunięcia zawodnika
    success_url = reverse_lazy('athlete_list')  # Po usunięciu wracamy na listę zawodników