# coding: utf-8

from django.contrib import admin

from game.pvp.models import Battle1x1

class Battle1x1Admin(admin.ModelAdmin):
    list_display = ('id', 'state', 'account', 'enemy', 'created_at')

admin.site.register(Battle1x1, Battle1x1Admin)
