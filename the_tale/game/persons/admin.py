# -*- coding: utf-8 -*-

from django.contrib import admin

from the_tale.game.persons import models


class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'place', 'state', 'type', 'name', 'power', 'created_at', 'out_game_at')

    list_filter = ('state', 'type', 'place')

    def name(self, obj):
        from the_tale.game.persons import logic
        return logic.load_person(model=obj).name


class SocialConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'connection', 'person_1', 'person_2', 'created_at')
    list_filter = ('state', 'connection')


admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.SocialConnection, SocialConnectionAdmin)
