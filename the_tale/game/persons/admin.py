# -*- coding: utf-8 -*-

from django.contrib import admin

from the_tale.game.persons.models import Person
from the_tale.game.persons.prototypes import PersonPrototype

class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'place', 'state', 'type', 'name', 'power', 'created_at', 'out_game_at')

    list_filter = ('state', 'type', 'place')

    def power(self, obj):
        person = PersonPrototype(obj)
        return person.power

admin.site.register(Person, PersonAdmin)
