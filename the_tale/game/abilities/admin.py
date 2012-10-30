# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import AbilityTask

class AbilityTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'hero', 'activated_at', 'available_at')

admin.site.register(AbilityTask, AbilityTaskAdmin)
