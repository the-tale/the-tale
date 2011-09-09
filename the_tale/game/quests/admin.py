# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Quest

class QuestAdmin(admin.ModelAdmin):
    list_display = ('id', 'percents', 'created_at', 'hero')


admin.site.register(Quest, QuestAdmin)
