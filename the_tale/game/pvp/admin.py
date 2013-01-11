# coding: utf-8

from django.contrib import admin

from game.pvp.models import Battle1x1

class Battle1x1Admin(admin.ModelAdmin):
    list_display = ('id', 'state', 'result', 'calculate_rating', 'account', 'enemy', 'created_at')

    list_filter= ('state', 'result')

admin.site.register(Battle1x1, Battle1x1Admin)
