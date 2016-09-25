# coding: utf-8

from django.contrib import admin

from the_tale.game.map.models import MapInfo, WorldInfo


class MapInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'turn_number')

class WorldInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

admin.site.register(MapInfo, MapInfoAdmin)
admin.site.register(WorldInfo, WorldInfoAdmin)
