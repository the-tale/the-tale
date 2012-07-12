# -*- coding: utf-8 -*-

from django.contrib import admin

from game.heroes.models import Hero, ChooseAbilityTask, ChoosePreferencesTask

class HeroAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'alive', 'health', 'angel_id')

    def angel_id(self, obj): return obj.angel_id

class ChooseAbilityTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'ability_id', 'comment')

class ChoosePreferencesTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'hero', 'state', 'preference_type', 'comment')


admin.site.register(Hero, HeroAdmin)
admin.site.register(ChooseAbilityTask, ChooseAbilityTaskAdmin)
admin.site.register(ChoosePreferencesTask, ChoosePreferencesTaskAdmin)
