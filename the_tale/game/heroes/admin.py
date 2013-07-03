# -*- coding: utf-8 -*-

from django.contrib import admin

from game.heroes.models import Hero

class HeroAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_alive', 'health', 'account')
    readonly_fields = ('created_at_turn', 'saved_at_turn', 'saved_at', 'account', 'pref_friend', 'pref_enemy')


admin.site.register(Hero, HeroAdmin)
