# coding: utf-8

from django.contrib import admin

from game.map.places.models import Place, Building


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'size', 'x', 'y')


class BuildingAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'person', 'type', 'x', 'y')


admin.site.register(Place, PlaceAdmin)
admin.site.register(Building, BuildingAdmin)
