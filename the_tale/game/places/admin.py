# coding: utf-8

from django.contrib import admin

from . import models
from . import logic


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_frontier', 'size', 'politic_power', 'x', 'y')

    list_filter = ('is_frontier',)

    def politic_power(self, obj):
        return logic.load_place(place_model=obj).politic_power

    def size(self, obj):
        return logic.load_place(place_model=obj).attrs.size

    def name(self, obj):
        return logic.load_place(place_model=obj).name


class BuildingAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'integrity', 'state', 'person', 'type', 'x', 'y')

    list_filter = ('state', 'type')


class ResourceExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'place_1', 'place_2', 'resource_1', 'resource_2', 'bill')


admin.site.register(models.Place, PlaceAdmin)
admin.site.register(models.Building, BuildingAdmin)
admin.site.register(models.ResourceExchange, ResourceExchangeAdmin)
