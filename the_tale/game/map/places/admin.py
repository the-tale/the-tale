# coding: utf-8

from django.contrib import admin

from the_tale.game.map.places.models import Place, Building, ResourceExchange
from the_tale.game.map.places import prototypes


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_frontier', 'size', 'x', 'y', 'power', 'raw_power', 'positive_bonus', 'negative_bonus')

    list_filter = ('is_frontier',)

    def power(self, obj):
        place = prototypes.PlacePrototype(obj)
        return int(place.power)

    def raw_power(self, obj):
        place = prototypes.PlacePrototype(obj)
        return int(place.raw_power)

    def positive_bonus(self, obj):
        place = prototypes.PlacePrototype(obj)
        return round(place.power_positive, 2)

    def negative_bonus(self, obj):
        place = prototypes.PlacePrototype(obj)
        return round(place.power_negative, 2)



class BuildingAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'integrity', 'state', 'person', 'type', 'x', 'y')

    list_filter = ('state', 'type')


class ResourceExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'place_1', 'place_2', 'resource_1', 'resource_2', 'bill')


admin.site.register(Place, PlaceAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(ResourceExchange, ResourceExchangeAdmin)
