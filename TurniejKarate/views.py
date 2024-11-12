from django.views.generic import TemplateView, ListView
from .models import Athlete

class HomeView(TemplateView):
    template_name = 'home.html'  # Ścieżka do szablonu strony głównej


class AthleteListView(ListView):
    model = Athlete
    template_name = 'athlete_list.html'  # Ścieżka do szablonu listy zawodników
    context_object_name = 'athletes'  # Nazwa, pod którą lista zawodników będzie dostępna w szablonie
