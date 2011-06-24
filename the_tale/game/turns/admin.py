# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Turn

class TurnAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

admin.site.register(Turn, TurnAdmin)

