# -*- coding: utf-8 -*-

from django.contrib import admin

from game.abilities.models import AbilitiesData

class AbilitiesDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'hero', 'help_available_at', 'arena_pvp_1x1_available_at')

admin.site.register(AbilitiesData, AbilitiesDataAdmin)
