# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Person

class PersonAdmin(admin.ModelAdmin):
    list_display = ('id','place', 'state', 'type', 'name', 'power')

    list_filter = ('state', 'type', 'place')

admin.site.register(Person, PersonAdmin)
