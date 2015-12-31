# coding: utf-8

from django.contrib import admin

from the_tale.game.heroes.models import Hero, HeroPreferences
from the_tale.game.heroes import logic as heroes_logic

class HeroAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_alive', 'health', 'account')
    readonly_fields = ('created_at_turn', 'saved_at_turn', 'saved_at', 'account')

    def name(self, obj):
        return heroes_logic.load_hero(hero_model=obj).name

class HeroPreferencesAdmin(admin.ModelAdmin):
    list_display = ('id', 'hero', 'energy_regeneration_type', 'mob', 'place', 'friend', 'enemy', 'equipment_slot')


admin.site.register(Hero, HeroAdmin)
admin.site.register(HeroPreferences, HeroPreferencesAdmin)
