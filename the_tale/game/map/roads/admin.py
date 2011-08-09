
# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Road, Waymark

class RoadAdmin(admin.ModelAdmin):
    list_display = ('id', 'point_1', 'point_2', 'length')

class WaymarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'point_from', 'point_to', 'road')

admin.site.register(Road, RoadAdmin)
admin.site.register(Waymark, WaymarkAdmin)


