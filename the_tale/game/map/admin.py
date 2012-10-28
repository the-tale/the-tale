# coding: utf-8

from django.contrib import admin

from game.map.models import MapInfo


class MapInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'turn_number')

admin.site.register(MapInfo, MapInfoAdmin)
