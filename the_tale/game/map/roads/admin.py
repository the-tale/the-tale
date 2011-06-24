
# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Road

class RoadAdmin(admin.ModelAdmin):
    list_display = ('point_1', 'point_2', 'length')

admin.site.register(Road, RoadAdmin)
