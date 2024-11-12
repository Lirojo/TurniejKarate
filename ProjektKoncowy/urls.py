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
from TurniejKarate.views import HomeView, AthleteListView, AthleteCreateView, AthleteUpdateView, AthleteDeleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),  # Strona główna
    path('athletes/', AthleteListView.as_view(), name='athlete_list'),  # Lista zawodników
    path('athletes/add/', AthleteCreateView.as_view(), name='athlete_create'),
    path('athletes/<int:pk>/edit/', AthleteUpdateView.as_view(), name='athlete_update'),  # Widok edytowania
    path('athletes/<int:pk>/delete/', AthleteDeleteView.as_view(), name='athlete_delete'),  # Widok usuwania
]
