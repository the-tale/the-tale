# -*- coding: utf-8 -*-

from django.contrib import admin

from game.persons.models import Person
from game.persons.prototypes import PersonPrototype

class PersonAdmin(admin.ModelAdmin):
    list_display = ('id','place', 'state', 'type', 'name', 'power')

    list_filter = ('state', 'type', 'place')

    def power(self, obj):
        person = PersonPrototype(obj)
        return person.power

admin.site.register(Person, PersonAdmin)
