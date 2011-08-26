# -*- coding: utf-8 -*-

from django.contrib import admin

from . import models

class ActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'percents', 'created_at', 'hero', 'order')

admin.site.register(models.Action, ActionAdmin)
