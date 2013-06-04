# coding: utf-8

from django.contrib import admin

from game.pvp.models import Battle1x1, Battle1x1Result

class Battle1x1Admin(admin.ModelAdmin):
    list_display = ('id', 'state', 'calculate_rating', 'account', 'enemy', 'created_at')

    list_filter = ('state',)

class Battle1x1ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'participant_1', 'participant_2', 'result', 'created_at')
    list_filter = ('result',)

admin.site.register(Battle1x1, Battle1x1Admin)
admin.site.register(Battle1x1Result, Battle1x1ResultAdmin)
