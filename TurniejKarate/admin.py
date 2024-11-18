from django.contrib import admin
from .models import Club, Athlete, Tournament, Round, WeightCategory

class AthleteAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'age', 'weight', 'gender', 'belt_level', 'karate_style', 'club')
    search_fields = ['first_name', 'last_name', 'club__name']

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'date')
    search_fields = ['name']

admin.site.register(Club)
admin.site.register(Athlete, AthleteAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Round)
admin.site.register(WeightCategory)
