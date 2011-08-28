
# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Place

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'subtype', 'size', 'x', 'y')

admin.site.register(Place, PlaceAdmin)

