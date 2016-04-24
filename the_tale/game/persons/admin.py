# -*- coding: utf-8 -*-

from django.contrib import admin

from . import models
from . import logic


class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'place', 'type', 'name', 'politic_power', 'created_at')

    list_filter = ('gender', 'race', 'type', 'place')

    def politic_power(self, obj):
        return logic.load_person(person_model=obj).politic_power

    def name(self, obj):
        return logic.load_person(person_model=obj).name


class SocialConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'connection', 'person_1', 'person_2', 'created_at')
    list_filter = ('state', 'connection')


admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.SocialConnection, SocialConnectionAdmin)
