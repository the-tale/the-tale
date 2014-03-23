# -*- coding: utf-8 -*-

from django.contrib import admin

from the_tale.game.persons.models import Person
from the_tale.game.persons.prototypes import PersonPrototype

class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'place', 'state', 'type', 'name', 'power', 'raw_power', 'positive_bonus', 'negative_bonus', 'created_at', 'out_game_at')

    list_filter = ('state', 'type', 'place')

    def power(self, obj):
        person = PersonPrototype(obj)
        return person.power

    def raw_power(self, obj):
        person = PersonPrototype(obj)
        return person.raw_power

    def positive_bonus(self, obj):
        person = PersonPrototype(obj)
        return round(person.power_positive, 2)

    def negative_bonus(self, obj):
        person = PersonPrototype(obj)
        return round(person.power_negative, 2)

    def name(self, obj):
        from the_tale.game.persons.prototypes import PersonPrototype
        return PersonPrototype(model=obj).name


admin.site.register(Person, PersonAdmin)
