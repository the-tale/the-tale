# coding: utf-8

from django.contrib import admin

from the_tale.game.map import models


class MapInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'turn_number', 'turn_number')

class WorldInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

class MapRegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'turn_number', 'created_at')


admin.site.register(models.MapInfo, MapInfoAdmin)
admin.site.register(models.WorldInfo, WorldInfoAdmin)
admin.site.register(models.MapRegion, MapRegionAdmin)
