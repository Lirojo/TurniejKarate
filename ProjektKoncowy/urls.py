"""
URL configuration for ProjektKoncowy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from TurniejKarate.views import (
    HomeView,
    AthleteListView,
    AthleteCreateView,
    AthleteUpdateView,
    AthleteDeleteView,
    TournamentListView,
    TournamentDetailView,
    RoundCreateView,
    RoundListView,
    add_round,
    add_athletes_to_tournament
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),  # Strona główna

    # Ścieżki dla logowania i wylogowywania
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Ścieżki dla zawodników (zabezpieczone logowaniem)
    path('athletes/', AthleteListView.as_view(), name='athlete_list'),  # Lista zawodników
    path('athletes/add/', AthleteCreateView.as_view(), name='athlete_create'),  # Dodanie zawodnika
    path('athletes/<int:pk>/edit/', AthleteUpdateView.as_view(), name='athlete_update'),  # Edytowanie zawodnika
    path('athletes/<int:pk>/delete/', AthleteDeleteView.as_view(), name='athlete_delete'),  # Usuwanie zawodnika

    # Ścieżki dla turniejów
    path('tournament/', TournamentListView.as_view(), name='tournament_list'),  # Lista turniejów
    path('tournament/<int:tournament_id>/', TournamentDetailView.as_view(), name='tournament_detail'),
    # Szczegóły turnieju

    # Ścieżka dla rund
    path('rounds/add/', RoundCreateView.as_view(), name='round_create'),  # Dodanie rundy
    path('add-round/', add_round, name='add_round'),  # Formularz dodawania rundy
    path('rounds/', RoundListView.as_view(), name='round_list'),  # Lista rund
    path('tournament/<int:tournament_id>/add-athletes/', add_athletes_to_tournament,
         # Przypisanie zawodników do turnieju
         name='add_athletes_to_tournament'),
]
